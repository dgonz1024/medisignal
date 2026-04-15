def build_page_params(page_token: str | None = None, page_size: int = 100) -> dict:
    params = {"pageSize": page_size}
    if page_token:
        params["pageToken"] = page_token
    return params

