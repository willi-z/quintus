from .walker import BasicDataWalker


class DataFiller(BasicDataWalker):
    def walk(self):
        for evaluation in self.evaluations:
            filters = evaluation.filter_per_args()
            keys = list(filters.keys())
            filters = list(filters.values())
            if len(filters) != 1:
                raise ValueError(
                    "DataFiller only works for evaluations with 1 required entity, "
                    + f"but {evaluation} requires {len(filters)}"
                )
            results = self.dataset.find(filters[0])
            for result in results:
                entries = evaluation.evaluate(**{keys[0]: result})
                unique_filter = None
                if result.get("_id"):
                    unique_filter = {"_id": {"$eq": result.get("_id")}}
                if unique_filter is None:
                    raise KeyError(
                        "Warning: Could not find unique filter for: " + f"{result}"
                    )

                for key, measurement in entries.items():
                    entry = measurement.dict(exclude_unset=True, exclude_none=True)
                    self.writer.write_entry({key: entry}, unique_filter)
                name = result["name"]
                print(f"updated: {name}")
