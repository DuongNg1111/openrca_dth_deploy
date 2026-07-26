import pandas as pd
from datetime import datetime

from src.schemas import (
    ParsedQuery,
    TimeWindow,
)

from src.input_module.telemetry_loader import connect_data_source
from src.input_module.metadata_loader import load_metadata
from src.process_module.preprocess import preprocess



def main():

    print("==============================")
    print(" MEMORY TEST ")
    print("==============================")


    # =====================================================
    # Fake Parsed Query
    # (simulate result after STEP 3)
    # =====================================================

    incident_time = datetime(
        2022,
        3,
        21,
        9,
        30
    )


    parsed_query = ParsedQuery(

        issue_key="DEV-112",

        environment="Cloud A",

        incident_description=
            "Unable to create shipping order",

        affected_system="Order",

        incident_time=incident_time,

        additional_information=None,


        keywords=[
            "unable",
            "create",
            "shipping",
            "order"
        ],


        time_window=TimeWindow(

            start=incident_time - pd.Timedelta(minutes=15),

            end=incident_time + pd.Timedelta(minutes=15)

        )
    )



    # =====================================================
    # STEP 5
    # Connect Data Source
    # =====================================================


    config = {

        "system": "Market",

        "data_root": "D:/"

    }


    data_source = connect_data_source(

        parsed_query,

        config

    )



    print("\nDATA SOURCE:")

    print(data_source)



    # =====================================================
    # STEP 6
    # Load Metadata
    # =====================================================


    metadata = load_metadata(

        data_source,

        parsed_query

    )


    print("\n==============================")
    print(" METADATA ")
    print("==============================")


    print(
        "Date Folder :",
        metadata.date
    )


    print(
        "Metric Files:",
        metadata.metric.count
    )


    print(
        "Log Files   :",
        metadata.log.count
    )


    print(
        "Trace Files :",
        metadata.trace.count
    )


    print(
        "Total Files :",
        metadata.total_files
    )



    # =====================================================
    # STEP 7
    # Preprocess
    # =====================================================


    print("\n==============================")
    print(" STEP 7: PREPROCESS ")
    print("==============================")


    preprocessed = preprocess(

        metadata,

        parsed_query

    )



    # =====================================================
    # MEMORY CHECK
    # =====================================================


    print("\n==============================")
    print(" MEMORY USAGE ")
    print("==============================")


    total_memory = 0



    print("\nMETRICS")

    for name, df in preprocessed.metrics.items():

        memory = (
            df.memory_usage(deep=True)
            .sum()
            /
            1024
            /
            1024
        )


        total_memory += memory


        print(
            f"{name:<25}: {memory:.2f} MB"
        )



    print("\nLOGS")

    for name, df in preprocessed.logs.items():

        memory = (
            df.memory_usage(deep=True)
            .sum()
            /
            1024
            /
            1024
        )


        total_memory += memory


        print(
            f"{name:<25}: {memory:.2f} MB"
        )



    print("\nTRACES")

    for name, df in preprocessed.traces.items():

        memory = (
            df.memory_usage(deep=True)
            .sum()
            /
            1024
            /
            1024
        )


        total_memory += memory


        print(
            f"{name:<25}: {memory:.2f} MB"
        )



    print("\n==============================")
    print(
        f"TOTAL MEMORY: {total_memory:.2f} MB"
    )
    print("==============================")



if __name__ == "__main__":
    main()