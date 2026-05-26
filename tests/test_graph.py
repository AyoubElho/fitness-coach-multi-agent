from graph import build_graph

def test_graph_compiles():
    graph = build_graph()
    assert graph is not None
    print("OK: graph compiled successfully.")

if __name__ == "__main__":
    test_graph_compiles()
