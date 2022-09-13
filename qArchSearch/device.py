import json
import pkgutil


class qcDeviceSet:
    """ QC device class.
    Contains the necessary parameters of the quantum hardware for OLSQ.
    """

    def __init__(self, name: str, nqubits: int = None, connection: list = None, extra_connection: list = None,
                 conflict_coupling_set: list = None):
        """ Create a QC device.
        The user can either input the device parameters, or use existing
        ones stored in olsq/devices/ in json format (especially for
        duplicating paper results).  The parameters of existing devices 
        are overriden if inputs are provided.

        Args:
            name: name for the device.  If it starts with "default_",
                use existing device; otherwise, more parameters needed.
            nqubits: (optional) the number of physical qubits.
            connection: set of edges connecting qubits.
            extra_connection: set of extra edges that can be added to the connection.
        """

        # typechecking for inputs
        if not isinstance(name, str):
            raise TypeError("name should be a string.")
        if nqubits is not None:
            if not isinstance(nqubits, int):
                raise TypeError("nqubits should be an integer.")
        
        if connection is not None:
            if not isinstance(connection, (list, tuple)):
                raise TypeError("connection should be a list or tuple.")
            else:
                for edge in connection:
                    if not isinstance(edge, (list, tuple)):
                        raise TypeError(f"{edge} is not a list or tuple.")
                    elif len(edge) != 2:
                        raise TypeError(f"{edge} does not connect two qubits.")
                    if not isinstance(edge[0], int):
                        raise TypeError(f"{edge[0]} is not an integer.")
                    if not isinstance(edge[1], int):
                        raise TypeError(f"{edge[1]} is not an integer.")
        
        if extra_connection is not None:
            if not isinstance(extra_connection, (list, tuple)):
                raise TypeError("connection should be a list or tuple.")
            else:
                for edge in extra_connection:
                    if not isinstance(edge, (list, tuple)):
                        raise TypeError(f"{edge} is not a list or tuple.")
                    elif len(edge) != 2:
                        raise TypeError(f"{edge} does not connect two qubits.")
                    if not isinstance(edge[0], int):
                        raise TypeError(f"{edge[0]} is not an integer.")
                    if not isinstance(edge[1], int):
                        raise TypeError(f"{edge[1]} is not an integer.")
        
        
        # set parameters from inputs with value checking
        self.name = name
        if nqubits is not None:
            self.count_physical_qubit = nqubits
        if "count_physical_qubit" not in self.__dict__:
            raise AttributeError("No physical qubit count specified.")

        if connection is not None:
            for edge in connection:
                if edge[0] < 0 or edge[0] >= self.count_physical_qubit:
                    raise ValueError( (f"{edge[0]} is outside of range "
                                       f"[0, {self.count_physical_qubit}).") )
                if edge[1] < 0 or edge[1] >= self.count_physical_qubit:
                    raise ValueError( (f"{edge[1]} is outside of range "
                                       f"[0, {self.count_physical_qubit}).") )
            self.list_qubit_edge = tuple( tuple(edge) for edge in connection)

        if extra_connection is not None:
            for edge in extra_connection:
                if edge[0] < 0 or edge[0] >= self.count_physical_qubit:
                    raise ValueError( (f"{edge[0]} is outside of range "
                                       f"[0, {self.count_physical_qubit}).") )
                if edge[1] < 0 or edge[1] >= self.count_physical_qubit:
                    raise ValueError( (f"{edge[1]} is outside of range "
                                       f"[0, {self.count_physical_qubit}).") )
            self.list_extra_qubit_edge = tuple( tuple(edge) for edge in extra_connection)
        
        self.conflict_coupling_set = []
        if conflict_coupling_set is not None:
            for edge_set in conflict_coupling_set:
                for edge in edge_set:
                    if edge[0] < 0 or edge[0] >= self.count_physical_qubit:
                        raise ValueError( (f"{edge[0]} is outside of range "
                                        f"[0, {self.count_physical_qubit}).") )
                    if edge[1] < 0 or edge[1] >= self.count_physical_qubit:
                        raise ValueError( (f"{edge[1]} is outside of range "
                                        f"[0, {self.count_physical_qubit}).") )
                self.conflict_coupling_set.append(edge_set)

        if "list_qubit_edge" not in self.__dict__:
            raise AttributeError("No edge set is specified.")
        
