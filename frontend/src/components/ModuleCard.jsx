import { useState } from "react";

const PRIORITY_STYLES = {
  1: { accent: "border-l-red-500",     badge: "bg-red-100 text-red-600",     dot: "bg-red-500",     label: "Needs Focus" },
  2: { accent: "border-l-amber-400",   badge: "bg-amber-100 text-amber-600", dot: "bg-amber-400",   label: "Review"      },
  3: { accent: "border-l-emerald-500", badge: "bg-emerald-100 text-emerald-600", dot: "bg-emerald-500", label: "Strong"  },
};

export default function ModuleCard({ module }) {
  const [open, setOpen] = useState(false);
  const style = PRIORITY_STYLES[module.priority] || PRIORITY_STYLES[2];

  return (
    <div className={`bg-white rounded-2xl border border-gray-100 shadow-sm border-l-4 ${style.accent} mb-3 overflow-hidden`}>
      {/* Header */}
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full text-left px-5 py-4 flex items-center justify-between gap-4 hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-3 min-w-0">
          <span className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 text-gray-500 text-xs font-bold flex items-center justify-center">
            {module.module_number}
          </span>
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-gray-800 font-semibold text-base leading-tight">
                {module.title}
              </h3>
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium flex-shrink-0 ${style.badge}`}>
                <span className={`inline-block w-1.5 h-1.5 rounded-full ${style.dot} mr-1 align-middle`}></span>
                {style.label}
              </span>
            </div>
            {!open && module.subtopics?.length > 0 && (
              <p className="text-xs text-gray-400 mt-0.5 truncate">
                {module.subtopics.slice(0, 3).join(" · ")}
                {module.subtopics.length > 3 && ` +${module.subtopics.length - 3} more`}
              </p>
            )}
          </div>
        </div>
        <span className={`flex-shrink-0 text-gray-400 transition-transform duration-300 ${open ? "rotate-180" : ""}`}>
          ▾
        </span>
      </button>

      {/* Expanded body — subtopics only, no resources */}
      {open && (
        <div className="px-5 pb-5 border-t border-gray-50">
          {module.subtopics?.length > 0 && (
            <div className="mt-4">
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                What to Study
              </p>
              <div className="flex flex-col gap-2">
                {module.subtopics.map((s, i) => (
                  <div key={i} className="flex items-start gap-3 text-sm text-gray-700">
                    <span className="mt-0.5 w-5 h-5 rounded-full bg-gray-100 text-gray-500 text-xs flex items-center justify-center flex-shrink-0 font-medium">
                      {i + 1}
                    </span>
                    <span className="leading-relaxed">{s}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}