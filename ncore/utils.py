def base_concrete_model(abstract, instance):
    """
    Used in methods of abstract models to find the super-most concrete
    (non abstract) model in the inheritance chain that inherits from the
    given abstract model. This is so the methods in the abstract model can
    query data consistently across the correct concrete model.

    Consider the following::

        class Abstract(models.Model)

            class Meta:
                abstract = True

            def concrete(self):
                return base_concrete_model(Abstract, self)

        class Super(Abstract):
            pass

        class Sub(Super):
            pass

        sub = Sub.objects.create()
        sub.concrete() # returns Super

    """

    for cls in reversed(instance.__class__.mro()):
        if issubclass(cls, abstract) and not cls._meta.abstract:
            return cls
    return instance.__class__


def get_unique_slug(Model, slug, pk):
    i = 0

    instance = (
        Model.objects.filter(slug__istartswith=slug + "-")
        .filter(slug__iregex=r"^{}-[0-9]+$".format(slug))
        .last()
    )

    if instance:
        # trying to get the last created instance for same slug
        # and instantiating i with its number suffix
        # e.g. slug: android-test, instance.slug = 'android-test-500'
        # then i will be set to 501
        # instance = Model.objects.filter(slug__istartswith=slug).last()
        slug_split = instance.slug.rsplit("-", 1)
        try:
            i = int(slug_split[1]) + 1
        except:
            i = 2
    elif Model.objects.filter(slug=slug).exists():
        # if slug without any suffix exists
        i = 2
    if i:
        # if a sequence number is found append it to slug
        slug = "%s-%s" % (slug, i)

    while True:
        if i > 0:
            if i > 1:
                slug = slug.rsplit("-", 1)[0]
            slug = "%s-%s" % (slug, i)
        qs = Model.objects.all()
        if pk is not None:
            qs = qs.exclude(pk=pk)
        if not qs.filter(slug=slug).exists():
            break
        i += 1
    return slug
