/**
 * What kind of failure a raw backend message describes. The error dialog leads with a specific,
 * actionable sentence for the kind instead of a generic "a bug happened", so the classifier errs
 * toward the most useful recovery: a failed download is a network problem before it is a model
 * problem, and a missing transcript file is a file problem before it is a model problem.
 */
export type ErrorKind = 'model' | 'network' | 'audio' | 'file' | 'disk' | 'memory' | 'managed' | 'unknown'

const PATTERNS: Array<[ErrorKind, RegExp]> = [
	['disk', /no space|disk full|not enough (?:disk )?space|quota|enospc|مساحة|قرص/i],
	['memory', /out of memory|memory allocation|cuda.*(?:memory|alloc|vram)|vram|failed to allocate|ذاكرة/i],
	['network', /network|internet|offline|download|connect|timed? ?out|dns|tls|ssl|http error|شبكة|اتصال|تنزيل|إنترنت|تحميل/i],
	['audio', /ffmpeg|codec|decode|\baudio\b|media|unsupported|صوت|ترميز|صيغة/i],
	['file', /no such file|not found|permission denied|access denied|invalid path|cannot open|failed to read|ملف|صلاحية/i],
	['model', /model|whisper|ggml|\.bin\b|\bvad\b|نموذج/i],
]

export function classifyError(log?: string): ErrorKind {
	if (!log) return 'unknown'
	for (const [kind, pattern] of PATTERNS) {
		if (pattern.test(log)) return kind
	}
	return 'unknown'
}
