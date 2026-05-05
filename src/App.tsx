import { useCallback, useEffect, useState } from 'react';
import MindMap, { type MindMapHandle } from './components/MindMap';
import Toolbar from './components/Toolbar';
import { loadMindMap } from './lib/loadData';
import type { MindMapData } from './lib/types';

type Status =
  | { kind: 'loading' }
  | { kind: 'ready'; data: MindMapData }
  | { kind: 'error'; message: string };

const THEME_KEY = 'brain-map.theme';

export default function App() {
  const [status, setStatus] = useState<Status>({ kind: 'loading' });
  const [handle, setHandle] = useState<MindMapHandle | null>(null);
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const stored = localStorage.getItem(THEME_KEY);
    if (stored === 'light' || stored === 'dark') return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  });

  useEffect(() => {
    const root = document.documentElement;
    root.classList.toggle('dark', theme === 'dark');
    localStorage.setItem(THEME_KEY, theme);
  }, [theme]);

  useEffect(() => {
    let cancelled = false;
    loadMindMap()
      .then((data) => {
        if (!cancelled) setStatus({ kind: 'ready', data });
      })
      .catch((err: Error) => {
        if (!cancelled) setStatus({ kind: 'error', message: err.message });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const onReady = useCallback((h: MindMapHandle) => setHandle(h), []);
  const onToggleTheme = useCallback(
    () => setTheme((t) => (t === 'dark' ? 'light' : 'dark')),
    [],
  );

  const title =
    status.kind === 'ready' ? status.data.title : 'Brain Map';
  const subtitle =
    status.kind === 'ready' ? status.data.subtitle : undefined;

  return (
    <>
      <Toolbar
        title={title}
        subtitle={subtitle}
        handle={handle}
        theme={theme}
        onToggleTheme={onToggleTheme}
      />
      <main className="relative flex-1 overflow-hidden">
        {status.kind === 'loading' && <CenteredMessage>Loading mind map…</CenteredMessage>}
        {status.kind === 'error' && (
          <CenteredMessage tone="error">
            <strong className="block text-base font-semibold">Couldn't load mindmap.json</strong>
            <span className="mt-2 block text-sm">{status.message}</span>
            <span className="mt-3 block text-xs text-slate-500 dark:text-slate-400">
              Edit <code>public/mindmap.json</code> and rebuild the container.
            </span>
          </CenteredMessage>
        )}
        {status.kind === 'ready' && <MindMap data={status.data} onReady={onReady} />}
      </main>
    </>
  );
}

function CenteredMessage({
  children,
  tone = 'info',
}: {
  children: React.ReactNode;
  tone?: 'info' | 'error';
}) {
  return (
    <div className="absolute inset-0 flex items-center justify-center p-6">
      <div
        className={
          tone === 'error'
            ? 'max-w-md rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-rose-900 shadow-sm dark:border-rose-900/60 dark:bg-rose-950/40 dark:text-rose-100'
            : 'rounded-lg border border-slate-200 bg-white px-4 py-3 text-slate-600 shadow-sm dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300'
        }
      >
        {children}
      </div>
    </div>
  );
}
