import { useEffect, useRef } from 'react';
import { Transformer } from 'markmap-lib';
import { Markmap, deriveOptions } from 'markmap-view';
import type { IPureNode } from 'markmap-common';
import type { MindMapData } from '../lib/types';
import { jsonToMarkdown } from '../lib/jsonToMarkdown';

export interface MindMapHandle {
  fit: () => void;
  zoomIn: () => void;
  zoomOut: () => void;
  expandAll: () => void;
  collapseAll: () => void;
}

interface Props {
  data: MindMapData;
  onReady?: (handle: MindMapHandle) => void;
}

const transformer = new Transformer();

export default function MindMap({ data, onReady }: Props) {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const mmRef = useRef<Markmap | null>(null);
  const rootRef = useRef<IPureNode | null>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const markdown = jsonToMarkdown(data);
    const { root } = transformer.transform(markdown);
    rootRef.current = root;

    const options = deriveOptions({
      colorFreezeLevel: 2,
      duration: 350,
      maxWidth: 320,
      paddingX: 12,
      spacingHorizontal: 90,
      spacingVertical: 12,
      initialExpandLevel: 2,
    });

    const mm = Markmap.create(svgRef.current, options, root);
    mmRef.current = mm;

    const handle: MindMapHandle = {
      fit: () => mm.fit(),
      zoomIn: () => mm.rescale(1.25),
      zoomOut: () => mm.rescale(0.8),
      expandAll: () => {
        if (!rootRef.current) return;
        walk(rootRef.current, (n) => {
          if (n.payload) n.payload.fold = 0;
          else n.payload = { fold: 0 };
        });
        void mm.setData(rootRef.current);
        void mm.fit();
      },
      collapseAll: () => {
        if (!rootRef.current) return;
        walk(rootRef.current, (n, depth) => {
          // Keep root expanded so the user can see top-level branches.
          const fold = depth >= 1 ? 1 : 0;
          if (n.payload) n.payload.fold = fold;
          else n.payload = { fold };
        });
        void mm.setData(rootRef.current);
        void mm.fit();
      },
    };

    onReady?.(handle);

    return () => {
      mm.destroy();
      mmRef.current = null;
      rootRef.current = null;
    };
  }, [data, onReady]);

  return <svg ref={svgRef} className="markmap-svg" />;
}

function walk(node: IPureNode, fn: (n: IPureNode, depth: number) => void, depth = 0) {
  fn(node, depth);
  if (node.children) {
    for (const child of node.children) walk(child, fn, depth + 1);
  }
}
