from py_eddy_tracker.data import get_remote_sample
from py_eddy_tracker.observations.network import Network, NetworkObservations

# Get identification data
file_objects = get_remote_sample(
    "eddies_med_adt_allsat_dt2018_err70_filt500_order1/Anticyclonic"
)

n = Network.from_eddiesobservations(file_objects, window=8)
# Group observations
group = n.group_observations(minimal_area=True)
e = n.build_dataset(group, raw_data=False)
# Segmentation
n = NetworkObservations.from_split_network(e, e.split_network(intern=False, window=8))
# save
n.write_file(
    filename="eddies_med_adt_allsat_dt2018_err70_filt500_order1/Anticyclonic_network.nc"
)
