from Dependencies import constants as c
import math

def validate_parameters(valid_resources, valid_prediction_types):
    """Decorator that ensures any functions in this section only use a valid resource and prediction type."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            resource = kwargs.get("resource")
            prediction_type = kwargs.get("prediction_type")
            if resource not in valid_resources:
                raise ValueError(f"Invalid resource: {resource}. Must be one of {valid_resources}.")
            if prediction_type not in valid_prediction_types or prediction_type != "all" or prediction_type != "none":
                raise ValueError(
                    f"Invalid prediction type: {prediction_type}. Must be one of {valid_prediction_types}.")
            return func(*args, **kwargs)

        return wrapper

    return decorator


# LEGACY
class CtFeEROI:
    """
    NOTE: This was written to model Court & Fizaine's work, but *was not used* in this thesis due to my
    adjusted methodology. This has been kept in for potential replication and comparisons in the future.
    """
    @validate_parameters(c.valid_resources, c.valid_prediction_types)
    def __init__(self, resource, prediction_type="none"):
        self.resource_dict = getattr(c, resource)
        self.prediction_type = prediction_type
        self.base_year = c.base_year

    def exploitation_ratio_cf(self, year):
        """An estimate of the exploitation ratio of a fossil fuel calculated by and based on Court and Fizaine's historical
        data. This follows a logistical growth/sigmoid function, and is used in the theoretical predictions of EROI."""

        def _exploitation_ratio_eq(year, prediction):
            return 1 + math.exp(
                -self.resource_dict["delta"][prediction] * (
                        year - self.base_year - self.resource_dict["tlag"][prediction]))

        if self.prediction_type == "all":
            exploitation_ratios = []
            for prediction in c.valid_prediction_types:
                exploitation_ratios += [_exploitation_ratio_eq(year, prediction)]
            return exploitation_ratios
        else:
            return [_exploitation_ratio_eq(year, self.prediction_type)]

    # def exploitation_ratio_adjusted(self, initial_year, current_year, dataset, year_column=0):
    #     """An estimate of the exploitation ratio of a fossil fuel calculated by and based on Court and Fizaine's historical
    #     data. This follows a logistical growth/sigmoid function, and is used in the theoretical predictions of EROI."""
    #
    #     def _exploitation_ratio_eq(year, initial_sum, total_sum):
    #         return 1 + math.exp(
    #             -self.resource_dict["delta"][prediction] * (
    #                     year - self.base_year - self.resource_dict["tlag"][prediction]))
    #
    #     if self.prediction_type == "all":
    #         exploitation_ratios = []
    #         for prediction in c.valid_prediction_types:
    #             exploitation_ratios += [_exploitation_ratio_eq(year, prediction)]
    #         return exploitation_ratios
    #     else:
    #         return [_exploitation_ratio_eq(year, self.prediction_type)]

    def resource_fossil_EROI(self, year):
        """An estimate of the EROI of a given fossil resource (coal, oil, or gas) from Court and Fizaine's
        predictions."""

        def _resource_fossil_EROI_eq(resource_er_value):
            return (((self.resource_dict["in"] +
                      (1 - self.resource_dict["in"]) / (
                              1 + math.exp(
                          -self.resource_dict["tl"] * (resource_er_value - self.resource_dict["me"])))) *
                     math.exp(self.resource_dict["rd"] * resource_er_value)) *
                    self.resource_dict["sf"])

        resource_fossil_EROIs = []
        resource_er = self.exploitation_ratio(year)

        if self.prediction_type == "none":
            pass
        if self.prediction_type == "all":
            for prediction_er in resource_er:
                resource_fossil_EROIs += [_resource_fossil_EROI_eq(prediction_er)]
            return resource_fossil_EROIs
        else:
            return _resource_fossil_EROI_eq(resource_er)
