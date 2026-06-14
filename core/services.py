from django.core.paginator import Paginator

from core.constants import PAGE_SIZE


def paginate_queryset(request, queryset, page_size=PAGE_SIZE):
    """Универсальная пагинация с учётом параметра 'page' из GET-запроса."""
    paginator = Paginator(queryset, page_size)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
