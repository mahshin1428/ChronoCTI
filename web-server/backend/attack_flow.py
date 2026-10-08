"""Evidence-preserving entity graph for the interactive report explorer."""
import networkx as nx


class AttackFlowEngine:
    def build_attack_flow_from_chrono_data(self, sentences, asset_map, technique_map):
        graph = nx.DiGraph()
        previous = []
        previous_sentence = None

        def connect(source, target, relation, evidence):
            if source == target:
                return
            if not graph.has_edge(source, target):
                graph.add_edge(source, target, relation=relation, evidence=[])
            items = graph.edges[source, target]["evidence"]
            for item in evidence:
                if item not in items:
                    items.append(item)

        for sentence in sentences:
            evidence = {"sentence_id": sentence["sentence_id"], "text": sentence["text"]}
            groups = {}
            for kind, key, names in [("technique", "techniques", technique_map), ("asset", "assets", asset_map)]:
                groups[kind] = []
                for item in sentence.get(key, []):
                    nid = f"{'tech' if kind == 'technique' else 'asset'}_{item['id']}"
                    groups[kind].append(nid)
                    if nid not in graph:
                        graph.add_node(nid, id=nid, type=kind, raw_id=item["id"],
                                       label=item.get("name") or names.get(item["id"], item["id"]),
                                       category="ATT&CK technique" if kind == "technique" else "Asset category",
                                       confidence=0.0, occurrence_count=0, evidence=[], prediction_sources=[])
                    node = graph.nodes[nid]
                    node["confidence"] = max(node["confidence"], item.get("confidence", 0.0))
                    if evidence not in node["evidence"]:
                        node["evidence"].append(evidence)
                        node["occurrence_count"] += 1
                    source = item.get("prediction_source", "classifier")
                    if source not in node["prediction_sources"]:
                        node["prediction_sources"].append(source)

            # Co-occurrence establishes an association, not a verified targeting claim.
            for technique in groups["technique"]:
                for asset in groups["asset"]:
                    connect(technique, asset, "CO_MENTIONED", [evidence])
            if groups["technique"]:
                for source in previous:
                    for target in groups["technique"]:
                        connect(source, target, "REPORT_ORDER", [previous_sentence, evidence])
                previous = groups["technique"]
                previous_sentence = evidence

        return self._layout(graph)

    def _layout(self, graph):
        techniques = [n for n in graph if graph.nodes[n]["type"] == "technique"]
        assets = [n for n in graph if graph.nodes[n]["type"] == "asset"]
        rank = {n: i for i, n in enumerate(techniques)}
        positions = {n: (100, 90 + i * 170) for i, n in enumerate(techniques)}
        asset_rank = {}
        for node in assets:
            parents = [rank[p] for p in graph.predecessors(node) if p in rank]
            asset_rank[node] = sum(parents) / len(parents) if parents else len(techniques)
        cursor = 90
        for node in sorted(assets, key=lambda n: (asset_rank[n], n)):
            y = max(cursor, 90 + asset_rank[node] * 170)
            positions[node] = (650, y)
            cursor = y + 150

        nodes = []
        for nid, data in graph.nodes(data=True):
            x, y = positions[nid]
            nodes.append({**data, "x": x, "y": y, "width": 280, "height": 112,
                          "subtitle": data["raw_id"], "sentence_id": data["evidence"][0]["sentence_id"],
                          "sentence_text": " | ".join(e["text"] for e in data["evidence"])})

        edges = []
        for index, (source, target, data) in enumerate(graph.edges(data=True)):
            association = data["relation"] == "CO_MENTIONED"
            edges.append({"id": f"edge_{index}", "source": source, "target": target,
                          **data, "edge_type": "association" if association else "narrative",
                          "label": "co-mentioned" if association else "next mention",
                          "basis": "Extracted from the same sentence; targeting is not verified." if association else
                          "Order of technique mentions in the report; execution order is not verified."})

        temporal = graph.subgraph(techniques)
        is_dag = nx.is_directed_acyclic_graph(temporal)
        return {"nodes": nodes, "edges": edges,
                "canvas_width": 1030, "canvas_height": max(500, max((n["y"] + 180 for n in nodes), default=0)),
                "metrics": {"total_nodes": len(nodes), "total_edges": len(edges),
                            "is_dag": is_dag, "longest_attack_chain": nx.dag_longest_path_length(temporal) if is_dag and techniques else 0,
                            "density": round(nx.density(graph), 4) if len(graph) > 1 else 0}}


attack_flow_engine = AttackFlowEngine()
