from __future__ import unicode_literals

from django.db import models


class BigIntegerPKModel(models.Model):
    """
    Use big integers as primary key
    (https://docs.djangoproject.com/es/1.10/ref/models/fields/#bigautofield)
    """
    id = models.BigAutoField(primary_key=True)

    class Meta:
        abstract = True


class Codesystem(BigIntegerPKModel):
    name = models.CharField(max_length=16, blank=True, null=True)
    oid = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'codesystem'

    def __str__(self):
        return 'name: %s, oid: %s' % (self.name, self.oid)


class Scriptelement(BigIntegerPKModel):
    titulo = models.CharField(max_length=64, blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    comentario = models.CharField(max_length=255, blank=True, null=True)
    html = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'scriptelement'

    def __str__(self):
        return '{} (version {})'.format(self.titulo, self.version)


class BaseHeaderOrFooter(BigIntegerPKModel):
    """
    Base (abstract) class for headers and footers,
    as they both have the same fields.
    """
    titulo = models.CharField(max_length=64, blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    comentario = models.CharField(max_length=255, blank=True, null=True)
    html = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} (version {})'.format(self.titulo, self.version)


class Header(BaseHeaderOrFooter):
    class Meta:
        db_table = 'header'


class Footer(BaseHeaderOrFooter):
    class Meta:
        db_table = 'footer'


class Articlehtml(BigIntegerPKModel):
    titulo = models.CharField(max_length=64, blank=True, null=True)
    descripcion = models.CharField(max_length=256, blank=True, null=True)
    html = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'articlehtml'

    def __str__(self):
        return 'Titulo: %s, descripcion: %s' % (self.titulo, self.descripcion)


class Code(BigIntegerPKModel):
    codesystem = models.ForeignKey('Codesystem', models.DO_NOTHING, db_column='fkcodesystem', blank=True, null=True)
    code = models.CharField(max_length=16, blank=True, null=True)
    displayname = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'code'

    def __str__(self):
        return 'code: %s, displayname: %s' % (self.code, self.displayname)


class Estudio(BigIntegerPKModel):
    modalidad = models.CharField(max_length=5, blank=True, null=True)
    code = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcode', blank=True, null=True)

    class Meta:
        db_table = 'estudio'


class Plantilla(BigIntegerPKModel):
    estudio = models.ForeignKey(Estudio, models.DO_NOTHING, db_column='fkestudio', blank=True, null=True)
    title = models.CharField(max_length=64, blank=True, null=True)
    type = models.CharField(max_length=64, blank=True, null=True)
    publisher = models.CharField(max_length=64, blank=True, null=True)
    rights = models.CharField(max_length=64, blank=True, null=True)
    licence = models.CharField(max_length=64, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    creator = models.CharField(max_length=64, blank=True, null=True)
    language = models.CharField(max_length=16, blank=True, null=True)
    title2 = models.CharField(max_length=64, blank=True, null=True)
    identifier = models.CharField(max_length=64, blank=True, null=True)
    cantidadfirmas = models.IntegerField(blank=True, null=True)
    urlparams = models.TextField(blank=True, null=True)

    # m2m relationships
    headers = models.ManyToManyField(Header, through='IntermediatePlantillaHeader')
    footers = models.ManyToManyField(Footer, through='IntermediatePlantillaFooter')
    headscripts = models.ManyToManyField(Scriptelement, through='IntermediateHeadScript', related_name='plantilla_head')
    bodyscripts = models.ManyToManyField(Scriptelement, through='IntermediateBodyScript', related_name='plantilla_body')

    class Meta:
        db_table = 'plantilla'

    def __str__(self):
        return self.title


class Plantillagruposldap(BigIntegerPKModel):
    plantilla = models.ForeignKey(Plantilla, models.DO_NOTHING, db_column='fkplantilla', blank=True, null=True)
    gdn = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'plantillagruposldap'


class Seccion(BigIntegerPKModel):
    section = models.ForeignKey('self', models.DO_NOTHING, db_column='fksection', blank=True, null=True)
    idseccion = models.CharField(max_length=4, blank=True, null=True)
    plantilla = models.ForeignKey(Plantilla, models.DO_NOTHING, db_column='fkplantilla', blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)
    templateuidroot = models.CharField(max_length=64, blank=True, null=True)
    selectcolor = models.CharField(max_length=16, blank=True, null=True)
    selecttitle = models.CharField(max_length=255, blank=True, null=True)
    inputchecked = models.CharField(max_length=2, blank=True, null=True)
    code = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcode', blank=True, null=True)
    articlehtml = models.ForeignKey(Articlehtml, models.DO_NOTHING, db_column='fkarticlehtml', blank=True, null=True)

    class Meta:
        db_table = 'seccion'


class Selectoption(BigIntegerPKModel):
    section = models.ForeignKey(Seccion, models.DO_NOTHING, db_column='fksection', blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)
    value = models.CharField(max_length=64, blank=True, null=True)
    text = models.CharField(max_length=64, blank=True, null=True)
    selected = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        db_table = 'selectoption'


class Entry(BigIntegerPKModel):
    element = models.CharField(max_length=16, blank=True, null=True)
    elementclasscode = models.CharField(max_length=8, blank=True, null=True)
    elementmoodcode = models.CharField(max_length=8, blank=True, null=True)
    templateuid = models.CharField(max_length=64, blank=True, null=True)
    identry = models.CharField(max_length=64, blank=True, null=True)
    code = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcode', blank=True, null=True)
    textreferencevalue = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'entry'


class Qualifier(BigIntegerPKModel):
    entry = models.ForeignKey(Entry, models.DO_NOTHING, db_column='fkentry', blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)
    code = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcode', blank=True, null=True)
    valueoriginaltext = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'qualifier'


class Value(BigIntegerPKModel):
    entry = models.ForeignKey(Entry, models.DO_NOTHING, db_column='fkentry', blank=True, null=True)
    type = models.CharField(max_length=8, blank=True, null=True)
    code = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcode', blank=True, null=True)
    unit = models.CharField(max_length=16, blank=True, null=True)
    value = models.CharField(max_length=64, blank=True, null=True)
    nullflavor = models.CharField(db_column='nullFlavor', max_length=16, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'value'


class Autenticado(BigIntegerPKModel):
    autenticado = models.ForeignKey('self', models.DO_NOTHING, db_column='fkautenticado', blank=True, null=True,
                                      related_name="autenticado_set")
    plantilla = models.ForeignKey('Plantilla', models.DO_NOTHING, db_column='fkplantilla', blank=True, null=True,
                                    related_name="plantilla")
    eiud = models.CharField(max_length=64, blank=True, null=True)
    eaccnum = models.CharField(max_length=16, blank=True, null=True)
    eaccoid = models.CharField(max_length=64, blank=True, null=True)
    urlparams = models.CharField(max_length=45, blank=True, null=True)
    activo = models.CharField(max_length=2, blank=True, null=True)
    pnombre = models.CharField(max_length=255, blank=True, null=True)
    pid = models.CharField(max_length=16, blank=True, null=True)
    poid = models.CharField(max_length=64, blank=True, null=True)
    psexo = models.CharField(max_length=1, blank=True, null=True)
    pnacimiento = models.CharField(max_length=8, blank=True, null=True)
    pbarrio = models.CharField(max_length=64, blank=True, null=True)
    pciudad = models.CharField(max_length=64, blank=True, null=True)
    pregion = models.CharField(max_length=64, blank=True, null=True)
    ppais = models.CharField(max_length=3, blank=True, null=True)
    efecha = models.DateTimeField(blank=True, null=True)
    eid = models.CharField(max_length=16, blank=True, null=True)
    erealizadoroid = models.CharField(max_length=64, blank=True, null=True)
    estudio = models.ForeignKey('Estudio', models.DO_NOTHING, db_column='fkestudio', blank=True, null=True)
    informetitulo = models.CharField(max_length=255, blank=True, null=True)
    informeuid = models.CharField(max_length=64, blank=True, null=True)
    custodianoid = models.CharField(max_length=64, blank=True, null=True)
    valoracion = models.CharField(max_length=64, blank=True, null=True)
    solicituduid = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'autenticado'


class Sec(BigIntegerPKModel):
    autenticado = models.ForeignKey(Autenticado, models.DO_NOTHING, db_column='fkautenticado', blank=True, null=True,
                                      related_name="secautenticado")
    compcode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcompcode', blank=True, null=True,
                                   related_name="seccompcode")
    templateuid = models.CharField(max_length=64, blank=True, null=True)
    idsec = models.CharField(max_length=4, blank=True, null=True)
    seccode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkseccode', blank=True, null=True,
                                  related_name="seccode")
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    entries = models.ManyToManyField(Entry, through='IntermediateSecEntry')

    class Meta:
        db_table = 'sec'


class Subsec(BigIntegerPKModel):
    compcode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcompcode', blank=True, null=True,
                                   related_name="fkcompcode")
    templateuid = models.CharField(max_length=64, blank=True, null=True)
    idsubsec = models.CharField(max_length=4, blank=True, null=True)  # (?)
    subseccode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fksubseccode', blank=True, null=True,
                                     related_name="fksubseccode")
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    parent_sec = models.ForeignKey(Sec, on_delete=models.DO_NOTHING, db_column='fksec', blank=True, null=True)
    entries = models.ManyToManyField(Entry, through='IntermediateSubSecEntry')

    class Meta:
        db_table = 'subsec'


class Subsubsec(BigIntegerPKModel):
    compcode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcompcode', blank=True, null=True,
                                   related_name="compcode")
    templateuid = models.CharField(max_length=64, blank=True, null=True)
    idsubsubsec = models.CharField(max_length=4, blank=True, null=True)  # (?)
    subsubseccode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fksubsubseccode', blank=True, null=True,
                                        related_name="subsubseccode")
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    parent_subsec = models.ForeignKey(Subsec, on_delete=models.DO_NOTHING, db_column='fksubsec', blank=True, null=True)
    entries = models.ManyToManyField(Entry, through='IntermediateSubSubSecEntry')

    class Meta:
        db_table = 'subsubsec'


class Firma(BigIntegerPKModel):
    informe = models.ForeignKey('Submit', models.DO_NOTHING, db_column='fkinforme', blank=True, null=True)
    md5 = models.CharField(max_length=45, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    udn = models.CharField(max_length=64, blank=True, null=True)
    uid = models.CharField(max_length=16, blank=True, null=True)
    uoid = models.CharField(max_length=64, blank=True, null=True)
    uname = models.CharField(max_length=255, blank=True, null=True)
    iname = models.CharField(max_length=255, blank=True, null=True)
    ioid = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'firma'


class Submit(BigIntegerPKModel):
    plantilla = models.ForeignKey(Plantilla, models.DO_NOTHING, db_column='fkplantilla', blank=True, null=True)
    eiud = models.CharField(max_length=64, blank=True, null=True)
    eaccnum = models.CharField(max_length=16, blank=True, null=True)
    eaccoid = models.CharField(max_length=64, blank=True, null=True)
    urlparamsenviado = models.TextField(blank=True, null=True)
    urlparamsrecibido = models.TextField(blank=True, null=True)
    listoparaautenticacion = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        db_table = 'submit'


################################################################################
# Intermediate models, to be used by many-to-many relationships

class BaseIntermediateHeaderOrFooter(BigIntegerPKModel):
    """
    Base (abstract) class for intermediate models to be
    used in many-to-many relationships between Plantilla
    and headers/footers, as they both have the same fields.
    """
    ordinal = models.IntegerField(blank=True, null=True)
    plantilla = models.ForeignKey(Plantilla, on_delete=models.DO_NOTHING, db_column='fkplantilla', blank=True, null=True)

    class Meta:
        abstract = True


class IntermediatePlantillaHeader(BaseIntermediateHeaderOrFooter):
    header = models.ForeignKey(Header, on_delete=models.DO_NOTHING, db_column='fkheader', blank=True, null=True)

    class Meta:
        db_table = 'plantillaheader'


class IntermediatePlantillaFooter(BaseIntermediateHeaderOrFooter):
    footer = models.ForeignKey(Footer, on_delete=models.DO_NOTHING, db_column='fkfooter', blank=True, null=True)

    class Meta:
        db_table = 'plantillafooter'


class BaseIntermediateScript(BigIntegerPKModel):
    """
    Base (abstract) class for intermediate models to be
    used in many-to-many relationships between Plantilla
    and scripts (head and body), as they both have the same fields.
    """
    script = models.ForeignKey(Scriptelement, on_delete=models.DO_NOTHING, db_column='fkscript', blank=True, null=True)
    plantilla = models.ForeignKey(Plantilla, on_delete=models.DO_NOTHING, db_column='fkplantilla', blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True


class IntermediateHeadScript(BaseIntermediateScript):
    class Meta:
        db_table = 'headscript'
        verbose_name = 'Head script'


class IntermediateBodyScript(BaseIntermediateScript):
    class Meta:
        db_table = 'bodyscript'
        verbose_name = 'Body script'


class BaseIntermediateSectionEntry(BigIntegerPKModel):
    """
    Base (abstract) class for intermediate models to be used in many-to-many relationships
    between sec/subsec/subsubsec and entry, as they all have the same fields.
    """
    ordinal = models.IntegerField(blank=True, null=True)
    entry = models.ForeignKey(Entry, on_delete=models.DO_NOTHING, db_column='fkentry', blank=True, null=True)

    class Meta:
        abstract = True


class IntermediateSecEntry(BaseIntermediateSectionEntry):
    sec = models.ForeignKey(Sec, on_delete=models.DO_NOTHING, db_column='fk', blank=True, null=True)

    class Meta:
        db_table = 'secentry'


class IntermediateSubSecEntry(BaseIntermediateSectionEntry):
    subsec = models.ForeignKey(Subsec, on_delete=models.DO_NOTHING, db_column='fk', blank=True, null=True)

    class Meta:
        db_table = 'subsecentry'


class IntermediateSubSubSecEntry(BaseIntermediateSectionEntry):
    subsubsec = models.ForeignKey(Subsubsec, on_delete=models.DO_NOTHING, db_column='fk', blank=True, null=True)

    class Meta:
        db_table = 'subsubsecentry'
