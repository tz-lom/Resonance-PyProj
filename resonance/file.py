import h5py
import resonance.db
import resonance.si
from typing import NoReturn, List, Tuple


def _hdf5_read_float64(
    group: h5py.Group, stream_name: str
) -> Tuple[resonance.si.Base, List[resonance.db.Base]]:
    stream_info = group["streamInfo"]
    blocks_descr = group["blocks"]
    data = group["data"]
    offset = 0
    si = resonance.si.Channels(
        stream_info["channels"][0], stream_info["samplingRate"][0], name=stream_name
    )
    blocks = []
    for created, received, size in blocks_descr:
        blocks.append(
            resonance.db.Channels(si, created, data[offset : offset + size, :])
        )
        offset = offset + size
    return si, blocks


def _hdf5_read_message(
    group: h5py.Group, stream_name: str
) -> Tuple[resonance.si.Base, List[resonance.db.Base]]:
    messages = group["messages"]
    si = resonance.si.Event(name=stream_name)
    blocks = []
    for created, received, msg in messages:
        blocks.append(resonance.db.Event(si, created, msg))
    return si, blocks


def _hdf5_read_events(group: h5py.Group, stream_name: str):
    return None, None


def hdf5(file_name: str) -> Tuple[List[resonance.si.Base], List[resonance.db.Base]]:
    f = h5py.File(file_name, "r")

    stream_info_list = []
    data_block_list = []

    def fail_on_unsupported_type(group: h5py.Group, name: str) -> NoReturn:
        raise Exception(
            "Unsupported type {0} of stream {1}".format(
                group["streamInfo"]["type"][0], name
            )
        )

    for stream_name in f.keys():
        group = f[stream_name]
        new_si, new_blocks = {
            b"Float64": _hdf5_read_float64,
            b"Message": _hdf5_read_message,
            b"EventBus": _hdf5_read_events,
        }.get(f[stream_name]["streamInfo"]["type"][0], fail_on_unsupported_type)(
            group, stream_name
        )
        if new_si is not None:
            stream_info_list.append(new_si)
            data_block_list = data_block_list + new_blocks

    return stream_info_list, resonance.db.sort_by_timestamp(data_block_list)
