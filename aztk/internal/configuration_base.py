import yaml
from aztk.error import AztkError, InvalidModelError


class ConfigurationBase:
    """
    Base class for any configuration.
    Include methods to help with validation
    """

    @classmethod
    def from_dict(cls, args: dict):
        """
        Create a new model from a dict values
        The dict is cleaned from null values and passed expanded to the constructor
        """
        try:
            return cls._from_dict(args)
        except (ValueError, TypeError) as e:
            pretty_args = yaml.dump(args, default_flow_style=False)
            raise AztkError("{0} {1}\n{2}".format(cls.__name__, str(e), pretty_args))

    @classmethod
    def _from_dict(cls, args: dict):
        clean = dict((k, v) for k, v in args.items() if v)
        return cls(**clean)

    def validate(self):
        raise NotImplementedError("Validate not implemented")

    def valid(self):
        try:
            self.validate()
            return True
        except AztkError:
            return False

    def _validate_required(self, attrs):
        for attr in attrs:
            if not getattr(self, attr):
                raise InvalidModelError("{0} missing {1}.".format(self.__class__.__name__, attr))

    def _merge_attributes(self, other, attrs):
        for attr in attrs:
            val = getattr(other, attr)
            if val is not None:
                setattr(self, attr, val)
