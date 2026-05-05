import type { MindMapData, MindNode } from './types';

function isMindNode(value: unknown): value is MindNode {
  if (!value || typeof value !== 'object') return false;
  const v = value as Record<string, unknown>;
  if (typeof v.title !== 'string' || v.title.length === 0) return false;
  if (v.note !== undefined && typeof v.note !== 'string') return false;
  if (v.children !== undefined) {
    if (!Array.isArray(v.children)) return false;
    if (!v.children.every(isMindNode)) return false;
  }
  return true;
}

function isMindMapData(value: unknown): value is MindMapData {
  if (!isMindNode(value)) return false;
  const v = value as unknown as Record<string, unknown>;
  if (v.subtitle !== undefined && typeof v.subtitle !== 'string') return false;
  return true;
}

export async function loadMindMap(url = '/mindmap.json'): Promise<MindMapData> {
  const res = await fetch(url, { cache: 'no-cache' });
  if (!res.ok) {
    throw new Error(`Failed to fetch ${url}: ${res.status} ${res.statusText}`);
  }
  let json: unknown;
  try {
    json = await res.json();
  } catch (err) {
    throw new Error(`Invalid JSON in ${url}: ${(err as Error).message}`);
  }
  if (!isMindMapData(json)) {
    throw new Error(
      `Schema mismatch in ${url}. Expected { title: string, subtitle?: string, note?: string, children?: MindNode[] } recursively.`,
    );
  }
  return json;
}
