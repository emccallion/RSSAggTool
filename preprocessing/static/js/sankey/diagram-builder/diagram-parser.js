/**
 * Parse Sankey diagram configuration text.
 */

export class DiagramParser {
    static parse(configText) {
        const lines = configText.split('\n');
        const flows = [];
        const nodeMap = new Map();
        const nodeColors = new Map();

        for (const line of lines) {
            const trimmed = line.trim();

            // Skip empty lines and comments
            if (!trimmed || trimmed.startsWith('//')) {
                continue;
            }

            // Parse color definition: :NodeName #color
            if (trimmed.startsWith(':')) {
                const [nodePart, colorPart] = trimmed.substring(1).split('#');
                if (nodePart && colorPart) {
                    const nodeName = nodePart.trim();
                    const color = '#' + colorPart.trim();
                    nodeColors.set(nodeName, color);
                }
                continue;
            }

            // Parse flow: Source [value] Target
            const flowMatch = trimmed.match(/^(.+?)\s*\[(\d+(?:\.\d+)?)\]\s*(.+)$/);
            if (flowMatch) {
                const source = flowMatch[1].trim();
                const value = parseFloat(flowMatch[2]);
                const target = flowMatch[3].trim();

                flows.push({ source, target, value });

                // Add nodes to map
                if (!nodeMap.has(source)) {
                    nodeMap.set(source, {
                        name: source,
                        color: nodeColors.get(source) || null
                    });
                }
                if (!nodeMap.has(target)) {
                    nodeMap.set(target, {
                        name: target,
                        color: nodeColors.get(target) || null
                    });
                }
            }
        }

        // Apply colors to nodes
        for (const [name, color] of nodeColors.entries()) {
            if (nodeMap.has(name)) {
                nodeMap.get(name).color = color;
            }
        }

        return { flows, nodeMap, nodeColors };
    }

    static extractNodes(config Text) {
        const { nodeMap } = this.parse(configText);
        return Array.from(nodeMap.values());
    }

    static buildConfigText(flows, nodeColors) {
        const lines = [];

        // Add flows
        for (const flow of flows) {
            lines.push(`${flow.source} [${flow.value}] ${flow.target}`);
        }

        // Add blank line if there are colors
        if (nodeColors.size > 0) {
            lines.push('');
        }

        // Add color definitions
        for (const [name, color] of nodeColors.entries()) {
            lines.push(`:${name} ${color}`);
        }

        return lines.join('\n');
    }

    static updateNodeColor(configText, nodeName, newColor) {
        const lines = configText.split('\n');
        let colorUpdated = false;

        // Try to update existing color definition
        const updatedLines = lines.map(line => {
            const trimmed = line.trim();
            if (trimmed.startsWith(':')) {
                const [nodePart] = trimmed.substring(1).split('#');
                if (nodePart && nodePart.trim() === nodeName) {
                    colorUpdated = true;
                    return `:${nodeName} ${newColor}`;
                }
            }
            return line;
        });

        // If color wasn't found, add it
        if (!colorUpdated) {
            updatedLines.push(`:${nodeName} ${newColor}`);
        }

        return updatedLines.join('\n');
    }
}
