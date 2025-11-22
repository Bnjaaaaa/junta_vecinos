def roles_context(request):
    user = request.user

    es_moderador = False
    es_admin = False

    if user.is_authenticated:
        es_moderador = user.groups.filter(name='Moderador').exists()
        es_admin = user.is_superuser

    return {
        'es_moderador': es_moderador,
        'es_admin': es_admin,
    }
