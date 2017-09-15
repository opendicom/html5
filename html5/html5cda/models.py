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
    category_choice = (
        ('relation', 'relation'),
        ('unit', 'unit'),
        ('other', 'other'),
    )
    translation = models.ForeignKey('self', models.DO_NOTHING, related_name="translation_code", blank=True, null=True)
    code = models.CharField(max_length=16, blank=True, null=True)
    displayname = models.CharField(max_length=255, blank=True, null=True)
    codesystem = models.ForeignKey('Codesystem', models.DO_NOTHING, blank=True, null=True)
    category = models.CharField(max_length=8, blank=True, null=True, choices=category_choice)

    class Meta:
        db_table = 'code'

    def __str__(self):
        return '{} ({})'.format(self.displayname, self.codesystem)


class Code1(BigIntegerPKModel):
    category_choice = (
        ('relation', 'relation'),
        ('unit', 'unit'),
        ('other', 'other'),
    )
    code = models.ForeignKey('Code', models.DO_NOTHING, blank=True, null=True)
    category = models.CharField(max_length=8, blank=True, null=True, choices=category_choice)

    class Meta:
        db_table = 'code1'

    def __str__(self):
        return '{} ({})'.format(self.code, self.category)


class Code2(BigIntegerPKModel):
    code1 = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True)
    rel = models.ForeignKey('Code', models.DO_NOTHING, blank=True, null=True, related_name="rel_code2")
    code = models.ForeignKey('Code', models.DO_NOTHING, blank=True, null=True, related_name="code_code2")

    class Meta:
        db_table = 'code2'

    def __str__(self):
        return '{} {} {}'.format(self.code1, self.rel, self.code)


class Code3(BigIntegerPKModel):
    code2 = models.ForeignKey('Code2', models.DO_NOTHING, blank=True, null=True)
    rel = models.ForeignKey('Code', models.DO_NOTHING, blank=True, null=True, related_name="rel_code3")
    code = models.ForeignKey('Code', models.DO_NOTHING, blank=True, null=True, related_name="code_code3")

    class Meta:
        db_table = 'code3'

    def __str__(self):
        return '{} {} {}'.format(self.code2, self.rel, self.code)


class Observation(BigIntegerPKModel):
    interpretation_choice = (
        ('B', 'B'), ('D', 'D'), ('U', 'U'), ('W', 'W'),
        ('<', '<'), ('>', '>'), ('A', 'A'), ('AA', 'AA'),
        ('HH', 'HH'), ('LL', 'LL'), ('H', 'H'), ('L', 'L'),
        ('N', 'N'), ('I', 'I'), ('MS', 'MS'), ('R', 'R'),
        ('S', 'S'), ('VS', 'VS'),
    )
    sec = models.ForeignKey('Sec', models.DO_NOTHING, blank=True, null=True)
    subsec = models.ForeignKey('Subsec', models.DO_NOTHING, blank=True, null=True)
    subsubsec = models.ForeignKey('Subsubsec', models.DO_NOTHING, blank=True, null=True)
    tbody = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True, related_name="tbody")
    tr = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True, related_name="tr")
    td = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True, related_name="td")
    code1 = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True)
    interpretationcode = models.CharField(max_length=2, choices=interpretation_choice, default="B")
    rel = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True, related_name="rel")
    list = models.ForeignKey('List', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'observation'


class List(BigIntegerPKModel):
    code1 = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'list'


class Item(BigIntegerPKModel):
    selected_choice = (
        (' selected="selected"', 'selected'),
        ('', 'none'),
    )
    disabled_choice = (
        (' disabled="disabled"', 'disabled'),
        ('', 'none'),
    )
    list = models.ForeignKey('List', models.DO_NOTHING, blank=True, null=True)
    number = models.SmallIntegerField(blank=True, null=True)
    selected = models.CharField(max_length=20, choices=selected_choice, default="")
    disabled = models.CharField(max_length=20, choices=disabled_choice, default="")
    code1 = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'item'


class Referencerange(BigIntegerPKModel):
    ucum_choice = (
        ('cm', 'cm'),
        ('', 'none'),
    )
    observation = models.ForeignKey('Observation', models.DO_NOTHING, blank=True, null=True)
    ucum = models.CharField(max_length=2, choices=ucum_choice, default="")
    low = models.FloatField(blank=True, null=True)
    high = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'referencerange'


class Value(BigIntegerPKModel):
    type_choice = (
        ('ED', 'ED'),
        ('BN', 'BN'),
        ('CD', 'CD'),
        ('CR', 'CR'),
        ('INT', 'INT'),
        ('REAL', 'REAL'),
        ('TS', 'TS'),
        ('PQ', 'PQ'),
    )
    observation = models.ForeignKey('Observation', models.DO_NOTHING, blank=True, null=True)
    xsitype = models.CharField(max_length=2, choices=type_choice, default="ED")
    item = models.ForeignKey('Item', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'value'


class Valueattribute(BigIntegerPKModel):
    value = models.ForeignKey('Value', models.DO_NOTHING, blank=True, null=True)
    content = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'valueattribute'


class Valuecontent(BigIntegerPKModel):
    value = models.ForeignKey('Value', models.DO_NOTHING, blank=True, null=True)
    content = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'valuecontent'


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
            if key not in ('xhtml5', 'cda', 'xsitype', 'array', 'list'):
                xhtml5 += ' {}={}'.format(key, json_value[key])
        xhtml5 += '>'
        if 'list' in json_value:
            items = Item.objects.filter(list=json_value['list']).order_by('number')
            for item in items:
                xhtml5 += '<option value="item/{}" {} {}>{}</option>'.format(item.id,
                                                                             item.selected,
                                                                             item.disabled,
                                                                             item.code1.code.displayname)
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
