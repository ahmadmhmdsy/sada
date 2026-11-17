//! Loopback request guard.
//!
//! `vibe-server` binds to loopback by default, where a web page can reach it the way any local
//! client can. What a page cannot do is choose the `Host` and `Origin` headers it sends: a browser
//! computes both from the URL and the page it runs on. DNS rebinding works by pointing an attacker
//! domain at 127.0.0.1, so requests still carry `Host: attacker.example` — this guard rejects those,
//! and rejects any request that carries a non-loopback `Origin` (that is what a cross-origin
//! `fetch`/form POST from an internet page looks like). Native clients (the Sada app, the CLI,
//! the MCP server, external integrations) send `Host: 127.0.0.1:<port>` or `localhost:<port>` and
//! no `Origin`, so they keep working unchanged.
//!
//! The guard only applies when the listener is on a loopback address. Binding elsewhere is an
//! explicit opt-in to serving other machines, and those requests legitimately carry the machine's
//! own address as `Host`.

use axum::extract::{Request, State};
use axum::http::{HeaderMap, HeaderValue, StatusCode, header};
use axum::middleware::Next;
use axum::response::{IntoResponse, Response};
use axum::Json;

/// State of the layer: the port the listener is bound to, which is the only port a loopback name
/// in `Host` may carry.
#[derive(Clone, Copy)]
pub(super) struct LoopbackGuard {
	pub(super) port: u16,
}

/// Reject requests that address this server by a name a browser page controls, or that come from
/// a page on another origin. Returns the inner response untouched for native loopback clients.
pub(super) async fn guard(State(state): State<LoopbackGuard>, request: Request, next: Next) -> Response {
	let headers = request.headers();
	if !host_allowed(headers, state.port) {
		tracing::warn!(
			host = ?headers.get(header::HOST),
			"rejected request: host is not a loopback name for this server"
		);
		return forbidden("request host is not allowed");
	}
	if !origin_allowed(headers.get(header::ORIGIN)) {
		tracing::warn!(origin = ?headers.get(header::ORIGIN), "rejected request: origin is not loopback");
		return forbidden("request origin is not allowed");
	}
	next.run(request).await
}

fn forbidden(message: &'static str) -> Response {
	(StatusCode::FORBIDDEN, Json(serde_json::json!({ "error": message }))).into_response()
}

/// True when `Host` is one of the loopback names for the listener's own port. Browsers always send
/// `Host`, so a missing value is rejected rather than treated as a native client.
fn host_allowed(headers: &HeaderMap, port: u16) -> bool {
	let Some(host) = headers.get(header::HOST).and_then(|value| value.to_str().ok()) else {
		return false;
	};
	let host = host.trim().to_ascii_lowercase();
	[
		format!("127.0.0.1:{port}"),
		format!("localhost:{port}"),
		format!("[::1]:{port}"),
	]
	.iter()
	.any(|allowed| *allowed == host)
}

/// True when there is no `Origin` (native clients) or it is a loopback page: the app dev server, a
/// local tool, or the Tauri webview. Anything else is a page from another origin.
fn origin_allowed(origin: Option<&HeaderValue>) -> bool {
	let Some(origin) = origin else {
		return true;
	};
	let Ok(origin) = origin.to_str() else {
		return false;
	};
	let origin = origin.trim().to_ascii_lowercase();
	let Some((scheme, rest)) = origin.split_once("://") else {
		return false;
	};
	if !matches!(scheme, "http" | "https" | "tauri") {
		return false;
	}
	let authority = rest.split('/').next().unwrap_or_default();
	// Userinfo in the authority would let `http://localhost@evil.example` pass the host check.
	if authority.contains('@') {
		return false;
	}
	let host = if authority.starts_with('[') {
		authority
			.split(']')
			.next()
			.map(|head| format!("{head}]"))
			.unwrap_or_default()
	} else {
		authority
			.rsplit_once(':')
			.map(|(host, _port)| host.to_string())
			.unwrap_or_else(|| authority.to_string())
	};
	matches!(host.as_str(), "127.0.0.1" | "localhost" | "[::1]" | "tauri.localhost")
}

#[cfg(test)]
mod tests {
	use super::*;
	use axum::body::Body;
	use axum::routing::get;
	use axum::Router;
	use http_body_util::BodyExt;
	use tower::ServiceExt;

	const PORT: u16 = 41_873;

	fn host_map(host: Option<&'static str>) -> HeaderMap {
		let mut headers = HeaderMap::new();
		if let Some(host) = host {
			headers.insert(header::HOST, HeaderValue::from_static(host));
		}
		headers
	}

	fn origin_map(origin: Option<&'static str>) -> HeaderMap {
		let mut headers = HeaderMap::new();
		if let Some(origin) = origin {
			headers.insert(header::ORIGIN, HeaderValue::from_static(origin));
		}
		headers
	}

	#[test]
	fn accepts_loopback_hosts_for_its_own_port() {
		for host in [
			"127.0.0.1:41873",
			"localhost:41873",
			"LOCALHOST:41873",
			"[::1]:41873",
		] {
			assert!(host_allowed(&host_map(Some(host)), PORT), "should accept {host}");
		}
	}

	#[test]
	fn rejects_hosts_a_page_controls() {
		for host in [
			None,
			Some("attacker.example:41873"),
			Some("127.0.0.1:1"),
			Some("127.0.0.1"),
			Some("127.0.0.1.evil.example:41873"),
			Some("localhost.evil.example:41873"),
			Some("0.0.0.0:41873"),
		] {
			assert!(!host_allowed(&host_map(host), PORT), "should reject host {host:?}");
		}
	}

	#[test]
	fn accepts_native_clients_without_an_origin() {
		assert!(origin_allowed(origin_map(None).get(header::ORIGIN)));
	}

	#[test]
	fn accepts_loopback_origins() {
		for origin in [
			"http://127.0.0.1:1420",
			"http://localhost:1420",
			"https://localhost",
			"http://[::1]:1420",
			"tauri://localhost",
			"http://tauri.localhost",
		] {
			let headers = origin_map(Some(origin));
			assert!(origin_allowed(headers.get(header::ORIGIN)), "should accept origin {origin}");
		}
	}

	#[test]
	fn rejects_origins_from_pages() {
		for origin in [
			"http://attacker.example",
			"https://attacker.example:443",
			"http://127.0.0.1.evil.example",
			"http://localhost@evil.example",
			"null",
			"ftp://127.0.0.1",
		] {
			let headers = origin_map(Some(origin));
			assert!(!origin_allowed(headers.get(header::ORIGIN)), "should reject origin {origin}");
		}
	}

	fn guarded_app() -> Router {
		Router::new()
			.route("/health", get(|| async { "ok" }))
			.layer(axum::middleware::from_fn_with_state(LoopbackGuard { port: PORT }, guard))
	}

	async fn status(app: Router, host: &'static str, origin: Option<&'static str>) -> StatusCode {
		let mut builder = Request::builder().uri("/health").method("GET").header(header::HOST, host);
		if let Some(origin) = origin {
			builder = builder.header(header::ORIGIN, origin);
		}
		let response = app.oneshot(builder.body(Body::empty()).unwrap()).await.unwrap();
		response.status()
	}

	#[tokio::test]
	async fn lets_native_requests_through() {
		let response = guarded_app()
			.oneshot(
				Request::builder()
					.uri("/health")
					.header(header::HOST, "127.0.0.1:41873")
					.body(Body::empty())
					.unwrap(),
			)
			.await
			.unwrap();
		assert_eq!(response.status(), StatusCode::OK);
		let body = response.into_body().collect().await.unwrap().to_bytes();
		assert_eq!(&body[..], b"ok");
	}

	#[tokio::test]
	async fn blocks_dns_rebinding_hosts() {
		assert_eq!(status(guarded_app(), "attacker.example:41873", None).await, StatusCode::FORBIDDEN);
	}

	#[tokio::test]
	async fn blocks_cross_origin_pages() {
		assert_eq!(
			status(guarded_app(), "127.0.0.1:41873", Some("http://attacker.example")).await,
			StatusCode::FORBIDDEN
		);
	}
}
