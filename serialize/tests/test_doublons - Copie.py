# import rapidjson
# from collections import deque
# from SmartFramework.tools.objects import (
##    class_str_from_class,
#   instance,
#   from_name,
# )  # ,from_id


# not_duplicates_types = set([type(None), bool, int, float, str])

# from __main__ import Root,Branch,Leaf


from SmartFramework.serialize import serializejson as serializejson


# --- TESTS -------------------------------------------------------
leaf_num = 0


class Root:
    def __init__(self):
        self.branch1 = Branch()
        self.branch2 = Branch()


class Branch:
    def __init__(self):
        self.leafs = [Leaf(), Leaf()]


class Leaf:
    def __init__(self):
        global leaf_num
        leaf_num += 1
        self.value = leaf_num


class Node:
    def __init__(self, **state):
        if state is not None:
            self.__dict__.update(state)
        pass

    def __serializejson__(self):
        return type(self), self.__dict__


class NodeA:
    def __init__(self):
        pass


class Node_reversed:
    def __init__(self):
        pass

    def __getstate__(self):
        return {k: v for k, v in sorted(self.__dict__.items(), reverse=True)}

    def __setstate__(self, state):
        self.__dict__ = state


class NodeB:
    def __init__(self):
        pass


class NodeC:
    def __init__(self):
        pass

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)


def exemple1():
    B = Node()
    A = [B, B]
    return A


def exemple1_dict():
    B = Node()
    A = {"premier": B, "second": B}
    return A


def exemple2():
    B = NodeB()
    A = NodeA()
    A.child2 = B
    A.child1 = B
    return A


def exemple2b():
    A = Node_reversed()
    B = Node()
    # C = Node()
    A.child2 = B
    A.child1 = B
    A.child3 = B
    return A


def exemple3():
    B = Node()
    A = Node()
    A.child = B
    B.child = A
    return A


def exemple4():
    A = Node()
    B = Node()
    C = Node()
    A.child1 = C
    C.child = B
    A.child2 = B
    return A


def exemple4b():
    A = Node_reversed()
    B = Node()
    C = Node()
    A.child1 = C
    C.child = B
    A.child2 = B
    A.child3 = B
    return A


def exemple4c():
    A = Node_reversed()
    B = NodeB()
    C = NodeC()
    A.child1 = B
    A.child2 = B
    A.child3 = C
    C.child = B
    return A


def exemple5():
    B = Node()
    A = [[[B], B]]
    return A


def exemple6():
    B = Node()
    A = Node()
    A.childs = [[[B], B]]
    return A


def exemple7():
    A = NodeA()
    B = NodeB()
    C = NodeC()
    A.childB = B
    B.childC = C
    C.childB = B
    A.childC = C
    return A


def exemple8():
    A = NodeA()
    A.childA = A
    return A


# B.coucou = "c'est moi"
# D = Node()
# A.child2 = {"key":B}
# A.child1 = {"key":B}

# C.child = D
# B = [1]
# B.child = A
# A = {"B":B,"B bis":B}

# dumped_jsonpickle = jsonpickle.dumps(A, indent="\t")
# print("jsonpickle ----------")
# print(dumped_jsonpickle)
for exemple in (
    # exemple1_dict,
    ##exemple1,
    # exemple2,
    # exemple2b,
    # exemple3,
    exemple4,
    # exemple4b,
    # exemple4c,
    # exemple5,
    # exemple6,
    # exemple7,
    # exemple8,
):  #:#,
    A = exemple()
    print(exemple.__name__, "-----------")
    print("dumped ---")
    # encoder = Encoder(indent="\t", sort_keys=True, ensure_ascii=False)
    dumped = serializejson.dumps(A)
    print(dumped)

    print("loaded ---")
    loaded = serializejson.loads(
        dumped,
        authorized_classes=[Root, Branch, Leaf, Node, NodeA, NodeB, NodeC, type(A)],
    )
    # print(serializejson.dumps(loaded))


# root = Root()
# root_dumped_before = serializejson.dumps(root)
# print("objet avant rehydratation :\n", root_dumped_before)
# print("id(root.branch2.leafs)", id(root.branch2.leafs))
# decoder = serializejson.Decoder()
# decoder.setUpdatables([Root, Branch, Leaf, list])  # Root,Branch,Leaf
##root_updated = decoder.update(root, saved)
##root_updated_dumped_for_print = rapidjson.dumps(root_updated, default=default_with_id, sort_keys=True, indent="\t")
# print("objet après rehydratation :\n", root_updated_dumped_for_print)
# print("id(root.branch2.leafs)",id(root.branch2.leafs))
# print(decoder.node_has_descendants_to_recreate)
