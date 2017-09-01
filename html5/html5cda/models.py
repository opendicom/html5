from __future__ import unicode_literals
from django.db import models
import json


class BigIntegerPKModel(models.Model):
    """
    Use big integers as primary key
    (https://docs.djangoproject.com/es/1.10/ref/models/fields/#bigautofield)
    """
    id = models.BigAutoField(primary_key=True)

    class Meta:
        abstract = True


class Codesystem(BigIntegerPKModel):
    oid = models.CharField(max_length=64, blank=True, null=True)
    version = models.CharField(max_length=16, blank=True, null=True)
    shortname = models.CharField(max_length=16, blank=True, null=True)
    hl7v2 = models.CharField(max_length=16, blank=True, null=True)
    dcm = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        db_table = 'codesystem'
        unique_together = ('oid',)

    def __str__(self):
        return self.shortname


class Code(BigIntegerPKModel):
    translation = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True, related_name="translation_code")
    code = models.CharField(max_length=16, blank=True, null=True)
    displayname = models.CharField(max_length=255, blank=True, null=True)
    codesystem = models.ForeignKey('Codesystem', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'code'

    def __str__(self):
        return '{} ({})'.format(self.displayname, self.codesystem)


class Node(BigIntegerPKModel):
    name = models.CharField(max_length=255, blank=True, null=True)
    super = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    code = models.ForeignKey('Code', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'node'

    def __str__(self):
        return '{}'.format(self.name)


class Observation(BigIntegerPKModel):
    sec = models.ForeignKey('Sec', models.DO_NOTHING, blank=True, null=True)
    subsec = models.ForeignKey('Subsec', models.DO_NOTHING, blank=True, null=True)
    subsubsec = models.ForeignKey('Subsubsec', models.DO_NOTHING, blank=True, null=True)
    ordinal = models.BigIntegerField(blank=True, null=True)
    node = models.ForeignKey(Node, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'observation'


class Referencerange(BigIntegerPKModel):
    observation = models.ForeignKey('Observation', models.DO_NOTHING, blank=True, null=True)
    node = models.ForeignKey('Node', models.DO_NOTHING, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    value = models.ForeignKey('Value', models.DO_NOTHING, blank=True, null=True)
    code = models.ForeignKey('Code', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'referencerange'


class Interpretationcode(BigIntegerPKModel):
    observation = models.ForeignKey('Observation', models.DO_NOTHING, blank=True, null=True)
    code = models.ForeignKey('Code', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'interpretationcode'


class Value(BigIntegerPKModel):
    type_choice = (
        ('BN', 'BN'),
        ('CD', 'CD'),
        ('CR', 'CR'),
        ('INT', 'INT'),
        ('REAL', 'REAL'),
    )
    observation = models.ForeignKey('Observation', models.DO_NOTHING, blank=True, null=True)
    xsitype = models.CharField(max_length=2, choices=type_choice, default="BL")
    node = models.ForeignKey('Node', models.DO_NOTHING, blank=True, null=True)
    value = models.CharField(max_length=255, blank=True, null=True)
    text = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'value'


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
    json = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'articlehtml'

    def __str__(self):
        return self.titulo

    def check_xhtml5(self):
        if 'xhtml5' in self.json:
            return 'YES'
        else:
            return None

    def get_xhtml5(self):
        return self.json2html5(json.loads(self.json))

    def json2html5(self, json_value):
        xhtml5 = '<{}'.format(json_value['xhtml5'])
        for key in json_value:
            if key not in ("xhtml5", "cda", "xsitype", "array"):
                xhtml5 += ' {}={}'.format(key,json_value[key])
        xhtml5 += '>'
        if 'array' in json_value:
            for key in json_value['array']:
                if type(key) == str:
                    xhtml5 += key
                else:
                    xhtml5 += self.json2html5(key)

        xhtml5 += '</{}>'.format(json_value['xhtml5'])
        return xhtml5


class Estudio(BigIntegerPKModel):
    modalidad = models.CharField(max_length=5, blank=True, null=True)
    code = models.ForeignKey(Code, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'estudio'

    def __str__(self):
        return '{} ({})'.format(self.code, self.modalidad)


class Plantilla(BigIntegerPKModel):
    estudio = models.ForeignKey(Estudio, models.DO_NOTHING, blank=True, null=True)
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
    plantilla = models.ForeignKey(Plantilla, models.DO_NOTHING, blank=True, null=True)
    gdn = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'plantillagruposldap'


class Section(BigIntegerPKModel):
    plantilla = models.ForeignKey(Plantilla, models.DO_NOTHING, blank=True, null=True)
    super = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)
    formatcode = models.ForeignKey(Code, models.DO_NOTHING, blank=True, null=True, related_name="formatcode")
    conceptcode = models.ForeignKey(Code, models.DO_NOTHING, blank=True, null=True, related_name="conceptcode")
    idattribute = models.CharField(max_length=4, blank=True, null=True)
    classattribute = models.CharField(max_length=16, blank=True, null=True)
    selectclass = models.CharField(max_length=16, blank=True, null=True)
    selectname = models.CharField(max_length=32, blank=True, null=True)
    selecttitle = models.CharField(max_length=255, blank=True, null=True)
    selectonchange = models.CharField(max_length=255, blank=True, null=True)
    article = models.ForeignKey(Articlehtml, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'section'

    def __str__(self):
        return '{} ({})'.format(self.idattribute, self.plantilla)

    # Permite obtener todas las subsecciones
    # http://stackoverflow.com/questions/4725343/django-self-recursive-foreignkey-filter-query-for-all-childs
    def get_all_sub_seccion(self, include_self=False):
        r = []
        if include_self:
            r.append(self)
        for item in Section.objects.filter(super=self).order_by('ordinal'):
            _r = item.get_all_sub_seccion(include_self=True)
            if 0 < len(_r):
                r.append(_r)
        return r

    def get_all_selectopcion(self):
        r = []
        for item in Selectoption.objects.filter(section=self).order_by('ordinal'):
            r.append(item)
        return r


class Selectoption(BigIntegerPKModel):
    section = models.ForeignKey(Section, models.DO_NOTHING, blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)
    value = models.CharField(max_length=64, blank=True, null=True)
    text = models.CharField(max_length=64, blank=True, null=True)
    selected = models.BooleanField(default=False)

    class Meta:
        db_table = 'selectoption'


class Autenticado(BigIntegerPKModel):
    autenticado = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True,
                                      related_name="autenticado_set")
    plantilla = models.ForeignKey('Plantilla', models.DO_NOTHING, blank=True, null=True,
                                    related_name="plantilla")
    eiud = models.CharField(max_length=64, blank=True, null=True)
    eaccnum = models.CharField(max_length=16, blank=True, null=True)
    eaccoid = models.CharField(max_length=64, blank=True, null=True)
    urlparams = models.TextField(blank=True, null=True)
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
    estudio = models.ForeignKey('Estudio', models.DO_NOTHING, blank=True, null=True)
    informetitulo = models.CharField(max_length=255, blank=True, null=True)
    informeuid = models.CharField(max_length=64, blank=True, null=True)
    custodianoid = models.CharField(max_length=64, blank=True, null=True)
    valoracion = models.CharField(max_length=64, blank=True, null=True)
    solicituduid = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'autenticado'


class Sec(BigIntegerPKModel):
    autenticado = models.ForeignKey(Autenticado, models.DO_NOTHING, blank=True, null=True)
    compcode = models.ForeignKey(Code, models.DO_NOTHING, blank=True, null=True, related_name="sec_compcode_set")
    templateuid = models.CharField(max_length=64, blank=True, null=True)
    idsec = models.CharField(max_length=4, blank=True, null=True)
    seccode = models.ForeignKey(Code, models.DO_NOTHING, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'sec'


class Subsec(BigIntegerPKModel):
    compcode = models.ForeignKey(Code, models.DO_NOTHING, blank=True, null=True, related_name="subsec_compcode_set")
    templateuid = models.CharField(max_length=64, blank=True, null=True)
    idsubsec = models.CharField(max_length=4, blank=True, null=True)  # (?)
    subseccode = models.ForeignKey(Code, models.DO_NOTHING, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    parent_sec = models.ForeignKey(Sec, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'subsec'


class Subsubsec(BigIntegerPKModel):
    compcode = models.ForeignKey(Code, models.DO_NOTHING, blank=True, null=True, related_name="subsubsec_compcode_set")
    templateuid = models.CharField(max_length=64, blank=True, null=True)
    idsubsubsec = models.CharField(max_length=4, blank=True, null=True)  # (?)
    subsubseccode = models.ForeignKey(Code, models.DO_NOTHING, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    parent_subsec = models.ForeignKey(Subsec, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'subsubsec'


class Firma(BigIntegerPKModel):
    informe = models.ForeignKey('Submit', models.DO_NOTHING, blank=True, null=True)
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
    plantilla = models.ForeignKey(Plantilla, models.DO_NOTHING, blank=True, null=True)
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
    plantilla = models.ForeignKey(Plantilla, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        abstract = True


class IntermediatePlantillaHeader(BaseIntermediateHeaderOrFooter):
    header = models.ForeignKey(Header, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'plantillaheader'


class IntermediatePlantillaFooter(BaseIntermediateHeaderOrFooter):
    footer = models.ForeignKey(Footer, on_delete=models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'plantillafooter'


class BaseIntermediateScript(BigIntegerPKModel):
    """
    Base (abstract) class for intermediate models to be
    used in many-to-many relationships between Plantilla
    and scripts (head and body), as they both have the same fields.
    """
    script = models.ForeignKey(Scriptelement, on_delete=models.DO_NOTHING, blank=True, null=True)
    plantilla = models.ForeignKey(Plantilla, on_delete=models.DO_NOTHING, blank=True, null=True)
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
