import Fuse, { type IFuseOptions } from 'fuse.js';
import type { MindMapData, MindNode } from './types';

interface FlatNode {
  id: string;
  title: string;
  note?: string;
  path: number[];
}

const FUSE_OPTIONS: IFuseOptions<FlatNode> = {
  keys: [
    { name: 'title', weight: 0.7 },
    { name: 'note', weight: 0.3 },
  ],
  // Lower threshold = stricter. Detail-node titles are 600+ chars long, so
  // Fuse's bitap algorithm at 0.4 over-matches dramatically. 0.25 still
  // tolerates 1-2 character typos on short queries (e.g. "Kubernets"
  // matches Kubernetes) without producing hundreds of false positives.
  threshold: 0.25,
  ignoreLocation: true,
  minMatchCharLength: 3,
  includeScore: false,
};

function flatten(root: MindMapData): FlatNode[] {
  const out: FlatNode[] = [];
  const walk = (node: MindNode, path: number[]) => {
    out.push({ id: path.join('.'), title: node.title, note: node.note, path });
    node.children?.forEach((c, i) => walk(c, [...path, i]));
  };
  walk(root, []);
  return out;
}

export interface SearchIndex {
  fuse: Fuse<FlatNode>;
  total: number;
}

export function buildIndex(root: MindMapData): SearchIndex {
  const flat = flatten(root);
  return { fuse: new Fuse(flat, FUSE_OPTIONS), total: flat.length };
}

function keptIdsFor(matched: FlatNode[]): Set<string> {
  const keep = new Set<string>();
  for (const m of matched) {
    for (let i = 0; i <= m.path.length; i++) {
      keep.add(m.path.slice(0, i).join('.'));
    }
  }
  return keep;
}

function prune(node: MindNode, kept: Set<string>, path: number[]): MindNode | null {
  if (!kept.has(path.join('.'))) return null;
  const children = node.children
    ?.map((c, i) => prune(c, kept, [...path, i]))
    .filter((c): c is MindNode => c !== null);
  return { ...node, children: children && children.length ? children : undefined };
}

export interface FilterResult {
  /** Pruned tree to render, or null when the filter matched nothing. */
  data: MindMapData | null;
  /** Number of nodes that matched the query (-1 = no filter active). */
  matchCount: number;
  /** True when a filter is currently applied. */
  active: boolean;
}

export function filterTree(
  root: MindMapData,
  index: SearchIndex,
  query: string,
): FilterResult {
  const trimmed = query.trim();
  if (!trimmed) {
    return { data: root, matchCount: -1, active: false };
  }
  const matched = index.fuse.search(trimmed).map((r) => r.item);
  if (matched.length === 0) {
    return { data: null, matchCount: 0, active: true };
  }
  const kept = keptIdsFor(matched);
  const pruned = prune(root, kept, []) as MindMapData;
  return { data: pruned, matchCount: matched.length, active: true };
}
