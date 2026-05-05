import type { MindMapHandle } from './MindMap';

interface Props {
  title: string;
  subtitle?: string;
  handle: MindMapHandle | null;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

export default function Toolbar({ title, subtitle, handle, theme, onToggleTheme }: Props) {
  return (
    <header className="sticky top-0 z-10 flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 bg-white/80 px-4 py-3 backdrop-blur dark:border-slate-800 dark:bg-slate-950/80 sm:px-6">
      <div className="flex items-center gap-3">
        <Logo />
        <div className="leading-tight">
          <h1 className="text-base font-semibold sm:text-lg">{title}</h1>
          {subtitle && (
            <p className="text-xs text-slate-500 dark:text-slate-400 sm:text-sm">{subtitle}</p>
          )}
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-1.5">
        <ToolbarButton onClick={() => handle?.expandAll()} disabled={!handle}>
          Expand all
        </ToolbarButton>
        <ToolbarButton onClick={() => handle?.collapseAll()} disabled={!handle}>
          Collapse all
        </ToolbarButton>
        <ToolbarButton onClick={() => handle?.fit()} disabled={!handle}>
          Fit
        </ToolbarButton>
        <div className="mx-1 hidden h-6 w-px bg-slate-200 dark:bg-slate-700 sm:block" />
        <ToolbarButton onClick={() => handle?.zoomOut()} disabled={!handle} aria-label="Zoom out">
          −
        </ToolbarButton>
        <ToolbarButton onClick={() => handle?.zoomIn()} disabled={!handle} aria-label="Zoom in">
          +
        </ToolbarButton>
        <div className="mx-1 hidden h-6 w-px bg-slate-200 dark:bg-slate-700 sm:block" />
        <ToolbarButton onClick={onToggleTheme} aria-label="Toggle theme">
          {theme === 'dark' ? '☀︎' : '☾'}
        </ToolbarButton>
      </div>
    </header>
  );
}

function ToolbarButton({
  children,
  onClick,
  disabled,
  ...rest
}: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className="inline-flex items-center justify-center rounded-md border border-slate-200 bg-white px-2.5 py-1.5 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 hover:text-slate-900 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800 dark:hover:text-white"
      {...rest}
    >
      {children}
    </button>
  );
}

function Logo() {
  return (
    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-pink-500 text-white shadow-sm">
      <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round">
        <circle cx="6" cy="12" r="2" fill="currentColor" />
        <circle cx="17" cy="6" r="1.6" fill="currentColor" />
        <circle cx="17" cy="12" r="1.6" fill="currentColor" />
        <circle cx="17" cy="18" r="1.6" fill="currentColor" />
        <path d="M8 12 Q12 12 15.5 6" />
        <path d="M8 12 H15.5" />
        <path d="M8 12 Q12 12 15.5 18" />
      </svg>
    </div>
  );
}
