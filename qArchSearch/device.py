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
            swap_duration: (optional) how many time units a SWAP takes.
            fmeas: (optional) measurement fidelity of each qubit.
            fsingle: (optional) single-qubit gate fidelity of each qubit
            ftwo: (optional) two-qubit gate fidelity of each edge.

        Example:
            To use existing "defualt_ourense" device
            >>> dev = qcdevice(name="default_ourense")
            To set up a new device
            >>> dev = qcdevice(name="dev", nqubits=5,
                    connection=[(0, 1), (1, 2), (1, 3), (3, 4)],
                    swap_duration=3)
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
        
        
        if name.startswith("default_"):
            # use an existing device
            f = pkgutil.get_data(__name__, "devices/" + name + ".json")
            data = json.loads(f)
            self.name = data["name"]
            self.count_physical_qubit = data["count_physical_qubit"]
            self.list_qubit_edge = tuple( tuple(edge)
                                          for edge in data["list_qubit_edge"])
            self.swap_duration = data["swap_duration"]
            if "list_fidelity_measure" in data:
                self.list_fidelity_measure = \
                    tuple(data["list_fidelity_measure"])
            if "list_fidelity_single" in data:
                self.list_fidelity_single = tuple(data["list_fidelity_single"])
            if "list_fidelity_two" in data:
                self.list_fidelity_two = tuple(data["list_fidelity_two"])
        else:
            self.name = name
        
        # set parameters from inputs with value checking
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
        
