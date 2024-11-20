import tempfile
from datetime import datetime
from glob import glob
from os.path import exists
from time import sleep

from dask.distributed import as_completed
from distributed import Client, LocalCluster
from py_eddy_tracker.dataset.grid import RegularGridDataset


def identification_(filename, cut, order, err=70):
    path_out = "eddies_med_adt_allsat_dt2018_err70_filt500_order1"
    date = filename.split("_")[-2]
    a_out = f"{path_out}/Anticyclonic_{cut:04}_err{err:03}_{date}.nc"
    c_out = f"{path_out}/Cyclonic_{cut:04}_err{err:03}_{date}.nc"
    if not exists(a_out) or not exists(c_out):
        g = RegularGridDataset(filename, "longitude", "latitude")
        g.add_uv("adt")
        g.bessel_high_filter("adt", cut, order=order)
        a, c = g.eddy_identification(
            "adt",
            "u",
            "v",
            datetime.strptime(date, "%Y%m%d"),
            shape_error=err,
            step=0.001,
            pixel_limit=(5, 2000),
            nb_step_to_be_mle=0,
            sampling=15,
            sampling_method="visvalingam",
        )
        out_name = f"%(path)s/%(sign_type)s_{cut:04}_err{err:03}_{date}.nc"
        a.write_file(path=path_out, filename=out_name)
        c.write_file(path=path_out, filename=out_name)

    sleep(0.01)
    return filename, cut


if __name__ == "__main__":
    log_dask = tempfile.tempdir
    kwargs = dict(
        local_directory=log_dask,
        log_directory=log_dask,
    )
    if True:
        import multiprocessing

        cluster = LocalCluster(
            int(multiprocessing.cpu_count() - 2),
            threads_per_worker=1,
            memory_limit="3GB",
        )
        client = Client(cluster)
    else:
        import dask_jobqueue

        cluster = dask_jobqueue.SGECluster(
            cores=1,
            memory="3GB",
            walltime=10000,
            resource_spec="mem_total=3G",
            **kwargs,
        )
        cluster.adapt(minimum_jobs=2, maximum_jobs=400)
        client = Client(cluster)

    print("dashboard : ", client.scheduler_info()["services"]["dashboard"])
    regexps = [
        "regional-mediterranean/dt-grids/all-sat-merged/200[345678]*/dt_med_allsat_phy_l4_*.nc"
    ]
    filenames = glob(regexps[0])
    futures = list()
    for filename in filenames:
        for i in [500]:
            r = client.submit(identification_, filename=filename, cut=i, order=1)
            futures.append(r)
    for future in as_completed(futures):
        if future.status == "error":
            print("---------------")
            print(future.key)
            print(future.exception())
            print("+++++++++++++++")
        else:
            # print(future.result())
            pass
    sleep(20)
    cluster.close()
    client.close()
