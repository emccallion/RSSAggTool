/**
 * State management for Sankey diagram builder.
 */

export class DiagramState {
    constructor(initialData = {}) {
        this.diagramId = initialData.diagramId || null;
        this.isPublished = initialData.isPublished || false;

        // Node and link state
        this.nodePositions = new Map();
        this.linkColors = new Map();
        this.canvasSize = {
            width: initialData.width || 1200,
            height: initialData.height || 600
        };

        // Interaction state
        this.currentColorNode = null;
        this.currentColorLink = null;
        this.renderTimeout = null;

        // Settings
        this.settings = {
            width: 1200,
            height: 600,
            nodeWidth: 15,
            nodePadding: 10,
            showNodes: true,
            showLabels: true,
            labelPosition: 'auto',
            ...initialData.settings
        };
    }

    // Node position methods
    updateNodePosition(nodeName, position) {
        this.nodePositions.set(nodeName, position);
    }

    getNodePosition(nodeName) {
        return this.nodePositions.get(nodeName);
    }

    hasNodePosition(nodeName) {
        return this.nodePositions.has(nodeName);
    }

    clearNodePositions() {
        this.nodePositions.clear();
    }

    // Link color methods
    updateLinkColor(linkKey, color) {
        this.linkColors.set(linkKey, color);
    }

    getLinkColor(linkKey) {
        return this.linkColors.get(linkKey);
    }

    hasLinkColor(linkKey) {
        return this.linkColors.has(linkKey);
    }

    clearLinkColors() {
        this.linkColors.clear();
    }

    // Canvas size methods
    updateCanvasSize(width, height) {
        const oldSize = { ...this.canvasSize };
        this.canvasSize = { width, height };
        return oldSize;
    }

    getCanvasSize() {
        return { ...this.canvasSize };
    }

    // Settings methods
    updateSetting(key, value) {
        this.settings[key] = value;
    }

    getSettings() {
        return { ...this.settings };
    }

    updateSettings(newSettings) {
        this.settings = { ...this.settings, ...newSettings };
    }

    // Snapshot methods for history
    getSnapshot() {
        return {
            positions: Object.fromEntries(this.nodePositions),
            linkColors: Object.fromEntries(this.linkColors),
            canvasSize: { ...this.canvasSize },
            settings: { ...this.settings }
        };
    }

    loadSnapshot(snapshot) {
        this.nodePositions = new Map(Object.entries(snapshot.positions || {}));
        this.linkColors = new Map(Object.entries(snapshot.linkColors || {}));
        this.canvasSize = snapshot.canvasSize || { width: 1200, height: 600 };
        this.settings = snapshot.settings || this.settings;
    }

    // Scale positions when canvas size changes
    scaleNodePositions(oldWidth, oldHeight, newWidth, newHeight) {
        const scaleX = newWidth / oldWidth;
        const scaleY = newHeight / oldHeight;

        const scaledPositions = new Map();
        for (const [name, pos] of this.nodePositions.entries()) {
            scaledPositions.set(name, {
                x: pos.x * scaleX,
                y: pos.y * scaleY
            });
        }
        this.nodePositions = scaledPositions;
    }
}
