import sys
import time

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as csv


def create_pyarrow_table(path="data/measurements.txt"):
    # Lê em blocos (streaming) para não carregar 1 bi de linhas na RAM
    reader = csv.open_csv(
        path,
        read_options=csv.ReadOptions(column_names=["station", "measure"], block_size=64 << 20),
        parse_options=csv.ParseOptions(delimiter=";"),
        convert_options=csv.ConvertOptions(column_types={"station": pa.string(), "measure": pa.float64()}),
    )
    # Agregação parcial por bloco: min, max, soma e contagem (média correta no final)
    partials = [
        pa.Table.from_batches([batch]).group_by("station").aggregate(
            [("measure", "min"), ("measure", "max"), ("measure", "sum"), ("measure", "count")]
        )
        for batch in reader
    ]
    final = pa.concat_tables(partials).group_by("station").aggregate(
        [("measure_min", "min"), ("measure_max", "max"), ("measure_sum", "sum"), ("measure_count", "sum")]
    )
    mean = pc.divide(final["measure_sum_sum"], final["measure_count_sum"])
    return pa.table({
        "station": final["station"],
        "min": final["measure_min_min"],
        "mean": pc.round(mean, 1),
        "max": final["measure_max_max"],
    }).sort_by("station")


if __name__ == "__main__":
    start_time = time.time()
    table = create_pyarrow_table(sys.argv[1] if len(sys.argv) > 1 else "data/measurements.txt")
    took = time.time() - start_time
    print(table.to_pandas())
    print(f"PyArrow Took: {took:.2f} sec")
