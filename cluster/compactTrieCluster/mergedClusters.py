import weakref
from easylogging.configLogger import get_logger_for_stdout
from text.phrases import phrase_to_string

__author__ = 'snorre'


class Component(object):
    def __init__(self):
        self.base_clusters = []
        self.next = None
        self.previous = None

    def delete(self):
        """
        Deletes a component from the component graph when merging ...
        """
        if self.previous() is not None:
            self.previous().next = self.next

        if self.next is not None:
            ## Use weakref to avoid circular references
            self.next.previous = self.previous


def generate_initial_components(base_clusters):

    component_index = []

    head = Component()
    x = head
    for base_cluster in base_clusters:
        new_component = Component()
        new_component.base_clusters = [base_cluster]
        new_component.previous = weakref.ref(x)
        x.next = new_component
        x = new_component
        component_index.append(new_component)
    head.next.previous = None
    return component_index


def merge(component1, component2):
    """
    :type component1: Component
    :param component1: first component
    :type component2: Component
    :param component2: second component
    :return: component1 with union of base clusters in component 1 and 2
    """
    for base_cluster in component2.base_clusters:
        if base_cluster not in component1.base_clusters:
            component1.base_clusters.append(base_cluster)


def merge_components(base_clusters, similarity_measurer):

    logger = get_logger_for_stdout("Merge Components")
    component_index = generate_initial_components(base_clusters)
    components = []
    base_index = []
    count = 0

    for _ in base_clusters:
        base_index.append(count)
        count += 1

    i = 0
    while i < count:
        j = i + 1
        while j < count:
            if base_index[i] != base_index[j] and \
                    similarity_measurer.similar(base_clusters[i], base_clusters[j]):
                if base_index[i] < base_index[j]:
                    min = base_index[i]
                    max = base_index[j]
                else:
                    min = base_index[j]
                    max = base_index[i]
                merge(component_index[min], component_index[max])
                component_index[max].delete()
                base_index[max] = base_index[min]
            j += 1
        i += 1
    logger.debug("Merging complete, make component list")
    component = component_index[0]
    while component is not None:
        components.append(component.base_clusters)
        component = component.next
    return components













