.method private static patch_filterVideoAdTriggers(Ljava/util/List;)Ljava/util/List;
    .registers 6

    # El kit no trae UI de ajustes: se fuerza el flag (el resto de la
    # logica, lista blanca incluida, sigue intacta en hideVideoAds).
    const/4 v5, 0x1

    sput-boolean v5, Lapp/morphe/extension/youtube/patches/ads/AdsPatch;->HIDE_VIDEO_ADS:Z

    invoke-static {}, Lapp/morphe/extension/youtube/patches/ads/AdsPatch;->hideVideoAds()Z

    move-result v0

    if-eqz v0, :cond_26

    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    invoke-interface {p0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v1

    const/16 v4, 0x6

    :cond_11
    :goto_11
    invoke-interface {v1}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    if-eqz v2, :cond_25

    invoke-interface {v1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Ladtl;

    iget v3, v2, Ladtl;->a:I

    if-ne v3, v4, :cond_11

    invoke-interface {v0, v2}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    goto :goto_11

    :cond_25
    return-object v0

    :cond_26
    return-object p0
.end method
