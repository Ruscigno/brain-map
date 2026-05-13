import { useRef } from 'react';
import type { MindMapHandle } from './MindMap';

interface Props {
  title: string;
  subtitle?: string;
  handle: MindMapHandle | null;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  // Search controls
  query: string;
  onQueryChange: (q: string) => void;
  onFilter: () => void;
  onClearFilter: () => void;
  filterActive: boolean;
  matchCount: number;
}

export default function Toolbar({
  title,
  subtitle,
  handle,
  theme,
  onToggleTheme,
  query,
  onQueryChange,
  onFilter,
  onClearFilter,
  filterActive,
  matchCount,
}: Props) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleClear = () => {
    onClearFilter();
    inputRef.current?.focus();
  };

  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
      {/* Row 1: title + view controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
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
      </div>

      {/* Row 2: search */}
      <div className="flex flex-wrap items-center gap-2 border-t border-slate-200 px-4 py-2 dark:border-slate-800 sm:px-6">
        <div className="relative min-w-[220px] flex-1 sm:max-w-md">
          <SearchIcon />
          <input
            ref={inputRef}
            type="search"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') onFilter();
              if (e.key === 'Escape' && filterActive) handleClear();
            }}
            placeholder="Search topics, definitions, examples… (fuzzy)"
            className="w-full rounded-md border border-slate-200 bg-white py-1.5 pl-8 pr-3 text-sm text-slate-900 shadow-sm placeholder:text-slate-400 focus:border-indigo-400 focus:outline-none focus:ring-1 focus:ring-indigo-400 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:placeholder:text-slate-500"
            aria-label="Search the mind map"
          />
        </div>
        <ToolbarButton onClick={onFilter} disabled={!query.trim()}>
          Filter
        </ToolbarButton>
        <ToolbarButton onClick={handleClear} disabled={!filterActive && !query}>
          Clear
        </ToolbarButton>
        {filterActive && (
          <span
            className={
              matchCount === 0
                ? 'ml-1 text-sm text-rose-600 dark:text-rose-400'
                : 'ml-1 text-sm text-slate-500 dark:text-slate-400'
            }
          >
            {matchCount === 0
              ? 'No matches'
              : `${matchCount} ${matchCount === 1 ? 'match' : 'matches'}`}
          </span>
        )}
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

function SearchIcon() {
  return (
    <svg
      viewBox="0 0 20 20"
      className="pointer-events-none absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400 dark:text-slate-500"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
    >
      <circle cx="9" cy="9" r="6" />
      <path d="M14 14 L18 18" />
    </svg>
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
