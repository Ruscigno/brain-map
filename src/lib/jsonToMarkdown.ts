import type { MindMapData, MindNode } from './types';

/**
 * Convert a MindMap tree to markdown that markmap-lib can parse.
 *
 * Strategy:
 *   - Root title becomes `# H1`.
 *   - Every other node is a nested bullet (`-`).
 *   - A node's `note` is emitted as the FIRST child bullet, italicized,
 *     so it's a sibling of any real children and can be expanded with them.
 */
export function jsonToMarkdown(data: MindMapData): string {
  const lines: string[] = [];
  lines.push(`# ${data.title}`);
  lines.push('');

  const renderChild = (node: MindNode, indent: number): void => {
    const pad = '  '.repeat(indent);
    lines.push(`${pad}- ${node.title}`);
    if (node.note) {
      lines.push(`${pad}  - *${escapeMarkdown(node.note)}*`);
    }
    if (node.children) {
      for (const child of node.children) {
        renderChild(child, indent + 1);
      }
    }
  };

  if (data.children) {
    for (const child of data.children) {
      renderChild(child, 0);
    }
  }

  return lines.join('\n');
}

/** Soften characters that would prematurely close italics or break lists. */
function escapeMarkdown(text: string): string {
  return text.replace(/\*/g, '\\*').replace(/\n+/g, ' ');
}
