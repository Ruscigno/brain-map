export interface MindNode {
  title: string;
  note?: string;
  children?: MindNode[];
}

export interface MindMapData extends MindNode {
  subtitle?: string;
}
