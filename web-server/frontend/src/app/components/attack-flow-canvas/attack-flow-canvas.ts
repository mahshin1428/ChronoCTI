import { AfterViewInit, Component, ElementRef, OnDestroy, ViewChild, computed, effect, input, signal, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AttackFlowGraph, AttackFlowNode, AttackFlowEdge } from '../../models/attack-flow.model';

@Component({
  selector: 'app-attack-flow-canvas', standalone: true, imports: [CommonModule, FormsModule],
  templateUrl: './attack-flow-canvas.html', styleUrl: './attack-flow-canvas.scss'
})
export class AttackFlowCanvasComponent implements AfterViewInit, OnDestroy {
  @ViewChild('svgRef') svgRef!: ElementRef<SVGSVGElement>;
  @ViewChild('containerRef') containerRef!: ElementRef<HTMLDivElement>;
  readonly graph = input<AttackFlowGraph | null>(null);
  readonly loading = input(false);
  query = signal('');
  showAssets = signal(true);
  showOrder = signal(true);
  selectedId = signal<string | null>(null);
  selectedEdgeId = signal<string | null>(null);
  exportError = signal('');
  transform = { x: 40, y: 40, scale: 1 };
  isPanning = false;
  private startPan = { x: 0, y: 0 };
  private observer?: ResizeObserver;
  private fitTimer?: ReturnType<typeof setTimeout>;
  readonly nodes = computed(() => (this.graph()?.nodes || []).filter(n => this.showAssets() || n.type !== 'asset'));
  readonly nodeMap = computed(() => new Map(this.nodes().map(n => [n.id, n])));
  readonly edges = computed(() => (this.graph()?.edges || []).filter(e => this.nodeMap().has(e.source) && this.nodeMap().has(e.target) && (this.showOrder() || e.edge_type !== 'narrative')));
  readonly selectedNode = computed(() => this.nodeMap().get(this.selectedId() || ''));
  readonly selectedEdge = computed(() => this.edges().find(e => e.id === this.selectedEdgeId()));
  readonly matchedIds = computed(() => new Set(this.nodes().filter(n => `${n.raw_id} ${n.label}`.toLowerCase().includes(this.query().trim().toLowerCase())).map(n => n.id)));
  readonly activeIds = computed(() => {
    const ids = new Set<string>();
    const node = this.selectedNode();
    const edge = this.selectedEdge();
    if (node) {
      ids.add(node.id);
      this.edges().filter(e => e.source === node.id || e.target === node.id).forEach(e => { ids.add(e.source); ids.add(e.target); });
    } else if (edge) { ids.add(edge.source); ids.add(edge.target); }
    return ids;
  });
  readonly connections = computed(() => this.edges().filter(e => e.source === this.selectedId() || e.target === this.selectedId()));

  constructor(private zone: NgZone) {
    effect(() => {
      this.graph();
      this.selectedId.set(null); this.selectedEdgeId.set(null); this.query.set('');
      clearTimeout(this.fitTimer);
      this.fitTimer = setTimeout(() => this.fitToScreen(false), 0);
    }, { allowSignalWrites: true });
  }
  ngAfterViewInit() {
    this.observer = new ResizeObserver(() => this.zone.run(() => this.fitToScreen(false)));
    this.observer.observe(this.containerRef.nativeElement);
  }
  ngOnDestroy() { this.observer?.disconnect(); clearTimeout(this.fitTimer); }
  clearSelection() { this.selectedId.set(null); this.selectedEdgeId.set(null); }
  selectNode(node: AttackFlowNode, event?: Event) { event?.stopPropagation(); this.selectedId.set(node.id); this.selectedEdgeId.set(null); }
  selectEdge(edge: AttackFlowEdge, event?: Event) { event?.stopPropagation(); this.selectedEdgeId.set(edge.id); this.selectedId.set(null); }
  toggleAssets() { this.showAssets.update(v => !v); this.clearSelection(); setTimeout(() => this.fitToScreen(false)); }
  toggleOrder() { this.showOrder.update(v => !v); this.clearSelection(); }
  dimNode(node: AttackFlowNode) { return !this.matchedIds().has(node.id) || (this.activeIds().size > 0 && !this.activeIds().has(node.id)); }
  dimEdge(edge: AttackFlowEdge) {
    if (this.query().trim() && !this.matchedIds().has(edge.source) && !this.matchedIds().has(edge.target)) return true;
    if (this.selectedEdge()) return edge.id !== this.selectedEdgeId();
    return !!this.selectedNode() && edge.source !== this.selectedId() && edge.target !== this.selectedId();
  }
  startPointer(event: PointerEvent) {
    if (event.button !== 0 || (event.target as Element).closest('[data-interactive]')) return;
    this.isPanning = true;
    this.startPan = { x: event.clientX - this.transform.x, y: event.clientY - this.transform.y };
    this.svgRef.nativeElement.setPointerCapture(event.pointerId);
  }
  movePointer(event: PointerEvent) {
    if (this.isPanning) this.transform = { ...this.transform, x: event.clientX - this.startPan.x, y: event.clientY - this.startPan.y };
  }
  endPointer() { this.isPanning = false; }
  onWheel(event: WheelEvent) {
    event.preventDefault();
    const rect = this.containerRef.nativeElement.getBoundingClientRect();
    this.zoom(event.deltaY < 0 ? 1.08 : 1 / 1.08, event.clientX - rect.left, event.clientY - rect.top);
  }
  zoom(factor: number, x?: number, y?: number) {
    const rect = this.containerRef.nativeElement.getBoundingClientRect();
    x ??= rect.width / 2; y ??= rect.height / 2;
    const scale = Math.min(2.5, Math.max(0.08, this.transform.scale * factor));
    this.transform = { x: x - (x - this.transform.x) * scale / this.transform.scale, y: y - (y - this.transform.y) * scale / this.transform.scale, scale };
  }
  bounds() {
    const nodes = this.nodes();
    return { x: -30, y: 0, width: Math.max(480, ...nodes.map(n => n.x + n.width + 100)) + 30,
      height: Math.max(400, ...nodes.map(n => n.y + n.height + 60)) };
  }
  fitToScreen(overview = true) {
    if (!this.containerRef || !this.nodes().length) return;
    const rect = this.containerRef.nativeElement.getBoundingClientRect();
    const bounds = this.bounds();
    const scale = Math.max(0.03, Math.min((rect.width - 45) / bounds.width, overview ? (rect.height - 90) / bounds.height : 0.9, 1.1));
    this.transform = { x: (rect.width - bounds.width * scale) / 2 - bounds.x * scale, y: 25, scale };
  }
  route(edge: AttackFlowEdge): { path: string; x: number; y: number } {
    const a = this.nodeMap().get(edge.source)!;
    const b = this.nodeMap().get(edge.target)!;
    if (b.type === 'asset') {
      const x1 = a.x + a.width, y1 = a.y + a.height / 2, x2 = b.x, y2 = b.y + b.height / 2;
      const mid = (x1 + x2) / 2;
      const t = 0.28 + (Number(edge.id.replace(/\D/g, '')) % 3) * 0.22, u = 1 - t;
      const labelX = u ** 3 * x1 + 3 * u * t * mid + t ** 3 * x2;
      const labelY = (u ** 3 + 3 * u * u * t) * y1 + (3 * u * t * t + t ** 3) * y2;
      return { path: `M ${x1} ${y1} C ${mid} ${y1}, ${mid} ${y2}, ${x2} ${y2}`, x: labelX, y: labelY };
    }
    if (b.y > a.y && b.y - a.y < 180) {
      const x = a.x + a.width / 2, y1 = a.y + a.height, y2 = b.y;
      return { path: `M ${x} ${y1} L ${x} ${y2}`, x, y: (y1 + y2) / 2 };
    }
    const y1 = a.y + a.height / 2, y2 = b.y + b.height / 2;
    const bend = 8 + (Number(edge.id.replace(/\D/g, '')) % 4) * 16;
    return { path: `M ${a.x} ${y1} C ${bend} ${y1}, ${bend} ${y2}, ${b.x} ${y2}`, x: (a.x + 3 * bend) / 4, y: (y1 + y2) / 2 };
  }
  wrapText(text: string): string[] {
    const lines: string[] = [];
    let line = '';
    for (const word of text.split(/\s+/)) {
      if ((line + ' ' + word).trim().length > 29 && line) { lines.push(line); line = ''; }
      line = (line + ' ' + word).trim();
    }
    if (line) lines.push(line);
    return lines.length > 2 ? [lines[0], lines[1].slice(0, 26) + '…'] : lines;
  }
  entityName(id: string) { return this.nodeMap().get(id)?.label || id; }
  techniqueUrl(node: AttackFlowNode) { return 'https://attack.mitre.org/techniques/' + node.raw_id.replace('.', '/') + '/'; }
  download(blob: Blob, extension: string) {
    const url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = `chronocti-graph.${extension}`; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  exportJson() { this.download(new Blob([JSON.stringify(this.graph(), null, 2)], { type: 'application/json' }), 'json'); }
  generateStandaloneSvgString() {
    const source = this.svgRef.nativeElement;
    const clone = source.cloneNode(true) as SVGSVGElement;
    const sourceElements = [source, ...Array.from(source.querySelectorAll('*'))];
    const cloneElements = [clone, ...Array.from(clone.querySelectorAll('*'))];
    const properties = ['fill', 'stroke', 'stroke-width', 'stroke-dasharray', 'opacity', 'font-family', 'font-size', 'font-weight', 'letter-spacing', 'text-anchor', 'paint-order'];
    sourceElements.forEach((element, i) => {
      const style = getComputedStyle(element);
      properties.forEach(property => (cloneElements[i] as SVGElement).style.setProperty(property, style.getPropertyValue(property)));
    });
    clone.querySelector('#viewport-group')?.removeAttribute('transform');
    clone.querySelectorAll('.hit-area').forEach(el => el.remove());
    clone.querySelectorAll('.entity-node, .edge').forEach(el => (el as SVGElement).style.opacity = '1');
    const b = this.bounds();
    clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    clone.setAttribute('viewBox', `${b.x} ${b.y} ${b.width} ${b.height}`);
    clone.setAttribute('width', String(b.width)); clone.setAttribute('height', String(b.height));
    clone.style.cssText = 'background:#0b1220;font-family:system-ui,sans-serif';
    const background = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    Object.entries({ x: b.x, y: b.y, width: b.width, height: b.height, fill: '#0b1220' }).forEach(([k,v]) => background.setAttribute(k, String(v)));
    clone.insertBefore(background, clone.firstChild);
    return { svgString: new XMLSerializer().serializeToString(clone), width: b.width, height: b.height };
  }
  exportSvg() { if (this.nodes().length) this.download(new Blob([this.generateStandaloneSvgString().svgString], { type: 'image/svg+xml' }), 'svg'); }
  exportPng() {
    if (!this.nodes().length) return;
    this.exportError.set('');
    const { svgString, width, height } = this.generateStandaloneSvgString();
    const scale = Math.min(2, 8192 / Math.max(width, height), Math.sqrt(16000000 / (width * height)));
    const canvas = document.createElement('canvas'); canvas.width = Math.ceil(width * scale); canvas.height = Math.ceil(height * scale);
    const image = new Image(); const url = URL.createObjectURL(new Blob([svgString], { type: 'image/svg+xml' }));
    image.onload = () => {
      try {
        const context = canvas.getContext('2d');
        if (!context) throw new Error('Canvas unavailable');
        context.drawImage(image, 0, 0, canvas.width, canvas.height);
        canvas.toBlob(blob => { if (blob) this.download(blob, 'png'); else this.exportError.set('Could not export PNG. Try SVG instead.'); });
      } catch { this.exportError.set('Could not export PNG. Try SVG instead.'); }
      finally { URL.revokeObjectURL(url); }
    };
    image.onerror = () => { URL.revokeObjectURL(url); this.exportError.set('Could not export PNG. Try SVG instead.'); };
    image.src = url;
  }
}
