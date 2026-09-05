import torch


def resolve_device(
    configured_device: str,
) -> torch.device:

    value = (
        configured_device
        .strip()
        .lower()
    )

    if value == "auto":

        if torch.cuda.is_available():

            return torch.device(
                "cuda"
            )

        return torch.device(
            "cpu"
        )

    if value == "cuda":

        if not torch.cuda.is_available():

            raise RuntimeError(
                "CLIP_DEVICE=cuda was requested "
                "but CUDA is not available in "
                "the current runtime."
            )

        return torch.device(
            "cuda"
        )

    if value == "cpu":

        return torch.device(
            "cpu"
        )

    raise ValueError(
        f"Unsupported device: {value}"
    )