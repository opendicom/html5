from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
import json
import re


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
    text = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'code1'

    def __str__(self):
        return '{} {} ({})'.format(self.text, self.code, self.category)

    def get_cda_format(self, observation=None):
        xml_cda = '<linkHtml'
        xml_cda += ' href="data:text/html,%3Cul%3E%3Cli%3E'
        xml_cda += 'code={}%3C%2Fli%3E%3Cli%3E'.format(self.code.code)
        xml_cda += 'codeSystem={}%3C%2Fli%3E%3Cli%3E'.format(self.code.codesystem.oid)
        xml_cda += 'codeSystemName={}%3C%2Fli%3E%3Cli%3E'.format(self.code.codesystem.shortname)
        xml_cda += 'displayName={}%3C%2Fli%3E%3C%2Ful%3E"'.format(self.code.displayname)
        if observation is not None:
            xml_cda += ' id="_{}">{}</linkHtml>'.format(observation.id, self.text)
        else:
            xml_cda += '>{}</linkHtml>'.format(self.text)
        return xml_cda


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
    sec = models.ForeignKey('Sec', models.DO_NOTHING, blank=True, null=True)
    subsec = models.ForeignKey('Subsec', models.DO_NOTHING, blank=True, null=True)
    subsubsec = models.ForeignKey('Subsubsec', models.DO_NOTHING, blank=True, null=True)
    label = models.ForeignKey('Label', models.DO_NOTHING, blank=True, null=True)
    option = models.ForeignKey('Option', models.DO_NOTHING, blank=True, null=True)
    col = models.ForeignKey('Col', models.DO_NOTHING, blank=True, null=True)
    row = models.ForeignKey('Row', models.DO_NOTHING, blank=True, null=True)
    table = models.ForeignKey('Table', models.DO_NOTHING, blank=True, null=True)
    code1 = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        db_table = 'observation'

    def get_cda_fomat_code1(self):
        xml_cda = '<entry>'
        xml_cda += ' <observation classCode="OBS" moodCode="EVN">'
        xml_cda += ' <code code="{}"'.format(self.code1.code.code)
        xml_cda += ' codeSystem="{}"'.format(self.code1.code.codesystem.oid)
        xml_cda += ' codeSystemName="{}"'.format(self.code1.code.codesystem.shortname)
        xml_cda += ' codeSystemVersion="{}"'.format(self.code1.code.codesystem.version)
        xml_cda += ' displayName="{}" />'.format(self.code1.code.displayname)
        xml_cda += ' <text><reference value="#_{}"/></text>'.format(self.id)
        xml_cda += ' </observation>'
        xml_cda += ' </entry>'
        return xml_cda

    def get_cda_format_select(self):
        xml_cda = '<entry>'
        xml_cda += ' <observation classCode="OBS" moodCode="EVN">'
        xml_cda += ' <code code="{}"'.format(self.label.code1.code.code)
        xml_cda += ' codeSystem="{}"'.format(self.label.code1.code.codesystem.oid)
        xml_cda += ' codeSystemName="{}"'.format(self.label.code1.code.codesystem.shortname)
        xml_cda += ' codeSystemVersion="{}"'.format(self.label.code1.code.codesystem.version)
        xml_cda += ' displayName="{}" />'.format(self.label.code1.code.displayname)
        xml_cda += ' <text><reference value="#_{}"/></text>'.format(self.id)
        xml_cda += ' <value xsi:type="CR">'
        xml_cda += ' <name code="{}"'.format(self.option.rel.code.code)
        xml_cda += ' codeSystem="{}"'.format(self.option.rel.code.codesystem.oid)
        xml_cda += ' codeSystemName="{}"'.format(self.option.rel.code.codesystem.shortname)
        xml_cda += ' codeSystemVersion="{}"'.format(self.option.rel.code.codesystem.version)
        xml_cda += ' displayName="{}" />'.format(self.option.rel.code.displayname)
        xml_cda += ' <value xsi:type="CD"'
        xml_cda += ' code="{}"'.format(self.option.code1.code.code)
        xml_cda += ' codeSystem="{}"'.format(self.option.code1.code.codesystem.oid)
        xml_cda += ' codeSystemName="{}"'.format(self.option.code1.code.codesystem.shortname)
        xml_cda += ' codeSystemVersion="{}"'.format(self.option.code1.code.codesystem.version)
        xml_cda += ' displayName="{}"'.format(self.option.code1.code.displayname)
        xml_cda += ' ></value>'  # Agregar qualifier o translation
        xml_cda += ' </value>'
        xml_cda += ' </observation>'
        xml_cda += ' </entry>'
        return xml_cda

    def get_cda_format_input(self):
        xml_cda = '<entry>'
        xml_cda += ' <observation classCode="OBS" moodCode="EVN">'
        xml_cda += ' <code code="{}"'.format(self.label.code1.code.code)
        xml_cda += ' codeSystem="{}"'.format(self.label.code1.code.codesystem.oid)
        xml_cda += ' codeSystemName="{}"'.format(self.label.code1.code.codesystem.shortname)
        xml_cda += ' codeSystemVersion="{}"'.format(self.label.code1.code.codesystem.version)
        xml_cda += ' displayName="{}" />'.format(self.label.code1.code.displayname)
        xml_cda += ' <text><reference value="#_{}"/></text>'.format(self.id)
        val_attr = Valueattribute.objects.get(observation=self)
        xml_cda += ' <value xsi:type="{}" {}="{}" />'.format(self.label.xsitype, val_attr.name, val_attr.content)
        xml_cda += ' </observation>'
        xml_cda += ' </entry>'
        return xml_cda


class Label(BigIntegerPKModel):
    category_choice = (
        ('patología', 'patología'),
    )
    xsitype_choice = (
        ('ED', 'ED'),
        ('BN', 'BN'),
        ('CD', 'CD'),
        ('CR', 'CR'),
        ('INT', 'INT'),
        ('REAL', 'REAL'),
        ('TS', 'TS'),
        ('PQ', 'PQ'),
    )
    code1 = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True)
    category = models.CharField(max_length=9, choices=category_choice)
    name = models.CharField(max_length=16, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    xsitype = models.CharField(max_length=4, choices=xsitype_choice)

    class Meta:
        db_table = 'label'

    def __str__(self):
        return '{} {}'.format(self.category, self.name)

    def get_label(self, idsection):
        xhtml = '<label>'
        xhtml += '<a href="label/{}/code1/{}?prettyxml">{}</a>'.format(self.id, self.code1.id, self.code1.text)
        if self.xsitype == 'CR':
            xhtml += '<a href="#" name="rel.href.{}.{}"></a>'.format(idsection, self.id)
        xhtml += '</label>'
        return xhtml

    def get_tag(self, idsection):
        xhtml = ''
        if self.xsitype == 'CR':
            xhtml = '<select name="{}.{}" >'.format(idsection, self.id)
            options = Option.objects.filter(label=self).order_by('number')
            for option in options:
                xhtml += '<option value="{}" {} {}>{}</option>'.format(option.id, option.selected,
                                                                       option.disabled, option.code1.text)
            xhtml += '</select>'
            return xhtml
        else:
            xhtml = '<input name="{}.{}"'.format(idsection, self.id)
            if self.xsitype == 'ED':
                xhtml += ' type="text"'
            elif self.xsitype == 'BN':
                xhtml += ' type="checkbox"'
            elif self.xsitype == 'TS':
                xhtml += ' type="datetime-local"'
            elif self.xsitype in 'INT REAL PQ CD':
                xhtml += ' type="number"'
                referenceranges = Referencerange.objects.filter(label=self)
                for referencerange in referenceranges:
                    xhtml += ' min="{}" max="{}"'.format(referencerange.low, referencerange.high)
            inputattributes = Inputattribute.objects.filter(label=self)
            for inputattribute in inputattributes:
                xhtml += ' {}={}'.format(inputattribute.name, inputattribute.content)
            xhtml += ' />'
        return xhtml

    def get_xhtml(self, idsection):
        return '{}{}'.format(self.get_label(idsection), self.get_tag(idsection))

    def get_cda_select(self, observation, caption=True):
        xhtml = '<list ID="_{}">'.format(observation.id)
        if caption is True:
            xhtml += '<caption>{}{}</caption>'.format(self.code1.get_cda_format(), observation.option.rel.get_cda_format())
        xhtml += '<item>{}</item>'.format(observation.option.code1.get_cda_format())
        xhtml += '</list>'
        return xhtml

    def get_cda_input(self, observation, input, caption=True):
        xhtml = '<list ID="_{}">'.format(observation.id)
        if caption is True:
            xhtml += '<caption>{}</caption>'.format(self.code1.get_cda_format())
        xhtml += '<item>{}</item>'.format(input)
        xhtml += '</list>'
        return xhtml

    def get_cda_label(self, observation=None):
        return self.code1.get_cda_format(observation=observation)


class WidgetSelect(Label):

    class Meta:
        proxy = True
        verbose_name = 'Widget Select'


    #def get_queryset(self):
    #    return super(WidgetSelect, self).get_queryset().filter(xsitype='CR')


class WidgetInput(Label):

    class Meta:
        proxy = True
        verbose_name = 'Widget Input'

    def __str__(self):
        return '{} {}'.format(self.name, self.xsitype)
    #def get_queryset(self):
    #    return super(WidgetInput, self).get_queryset().exclude(xsitype='CR')


class Option(BigIntegerPKModel):
    selected_choice = (
        (' selected="selected"', 'selected'),
        (' ', 'none'),
    )
    disabled_choice = (
        (' disabled="disabled"', 'disabled'),
        (' ', 'none'),
    )
    interpretation_choice = (
        ('B', 'B'), ('D', 'D'), ('U', 'U'), ('W', 'W'),
        ('<', '<'), ('>', '>'), ('A', 'A'), ('AA', 'AA'),
        ('HH', 'HH'), ('LL', 'LL'), ('H', 'H'), ('L', 'L'),
        ('N', 'N'), ('I', 'I'), ('MS', 'MS'), ('R', 'R'),
        ('S', 'S'), ('VS', 'VS'),
    )
    label = models.ForeignKey('Label', models.DO_NOTHING, blank=True, null=True)
    number = models.SmallIntegerField(blank=True, null=True)
    selected = models.CharField(max_length=20, choices=selected_choice, default="", blank=True)
    disabled = models.CharField(max_length=20, choices=disabled_choice, default="", blank=True)
    code1 = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True, related_name="code1")
    rel = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True, related_name="code1_rel")
    interpretationcode = models.CharField(max_length=2, choices=interpretation_choice, default="B")

    class Meta:
        db_table = 'option'


class Referencerange(BigIntegerPKModel):
    ucum_choice = (
        ('cm', 'cm'),
        ('', 'none'),
    )
    label = models.ForeignKey('Label', models.DO_NOTHING, blank=True, null=True)
    ucum = models.CharField(max_length=2, choices=ucum_choice, default="")
    low = models.FloatField(blank=True, null=True)
    high = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = 'referencerange'


class Inputattribute(BigIntegerPKModel):
    label = models.ForeignKey('Label', models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=32, blank=True, null=True)
    content = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'inputattribute'


class Valueattribute(BigIntegerPKModel):
    observation = models.ForeignKey('Observation', models.DO_NOTHING, blank=True, null=True)
    content = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        db_table = 'valueattribute'


class Table(BigIntegerPKModel):
    code1 = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True)
    category = models.CharField(max_length=1, blank=True, null=True)
    name = models.CharField(max_length=16, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'table'
        verbose_name = 'Widget Table'

    def __str__(self):
        return '{} {}'.format(self.category, self.name)

    def get_xhtml(self, idsection):
        xhtml5 = '<table border="1"><thead><tr><th></th>'
        cols = Col.objects.filter(table=self).order_by('number')
        for col in cols:
            xhtml5 += '<td>'
            if col.label is not None:
                xhtml5 += col.label.get_label(idsection=idsection)
            elif col.code1 is not None:
                xhtml5 += col.get_code1(idsection=idsection)
            else:
                xhtml5 += col.content
            xhtml5 += '</td>'
        xhtml5 += '</tr></thead><tbody>'
        rows = Row.objects.filter(table=self).order_by('number')
        for row in rows:
            xhtml5 += '<tr><th>'
            if row.label is not None:
                xhtml5 += row.label.get_label(idsection=idsection)
            elif row.code1 is not None:
                xhtml5 += row.get_code1(idsection=idsection)
            else:
                xhtml5 += row.content
            xhtml5 += '</th>'
            for col in cols:
                xhtml5 += '<td>'
                try:
                    cell = Cell.objects.get(row=row, col=col)
                    if cell.label is not None:
                        if row.label is not None or col.label is not None:
                            xhtml5 += cell.label.get_tag(idsection=idsection)
                        else:
                            xhtml5 += cell.label.get_xhtml(idsection=idsection)
                    elif cell.code1 is not None:
                        xhtml5 += cell.get_code1(idsection=idsection)
                    else:
                        xhtml5 += cell.content
                except:
                    print('Missing cell config')
                xhtml5 += '</td>'
            xhtml5 += '</tr>'
        xhtml5 += '</tbody></table>'
        return xhtml5


class Col(BigIntegerPKModel):
    table = models.ForeignKey('Table', models.DO_NOTHING, blank=True, null=True)
    number = models.BigIntegerField(blank=True, null=True)
    label = models.ForeignKey('Label', models.DO_NOTHING, blank=True, null=True)
    code1 = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True)
    content = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'col'

    def __str__(self):
        return '{} {}'.format(self.table, self.number)

    def get_code1(self, idsection):
        xhtml = '<label>'
        xhtml += '<a href="label/{}/code1/{}?prettyxml">{}</a>'.format(self.id, self.code1.id, self.code1.text)
        xhtml += '<a href="#" name="option.href.{}.{}"></a>'.format(idsection, self.id)
        xhtml += '</label>'
        return xhtml

    def get_content_cda(self):
        xhtml = '<content>{}</content>'.format(self.content)
        return xhtml

    def get_label_cda(self):
        return self.code1.get_cda_format()


class Row(BigIntegerPKModel):
    table = models.ForeignKey('Table', models.DO_NOTHING, blank=True, null=True)
    number = models.BigIntegerField(blank=True, null=True)
    label = models.ForeignKey('Label', models.DO_NOTHING, blank=True, null=True)
    code1 = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True)
    content = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'row'

    def __str__(self):
        return '{} {}'.format(self.table, self.number)

    def get_code1(self, idsection):
        xhtml = '<label>'
        xhtml += '<a href="label/{}/code1/{}?prettyxml">{}</a>'.format(self.id, self.code1.id, self.code1.text)
        xhtml += '<a href="#" name="option.href.{}.{}"></a>'.format(idsection, self.id)
        xhtml += '</label>'
        return xhtml

    def get_content_cda(self):
        xhtml = '<content>{}</content>'.format(self.content)
        return xhtml

    def get_label_cda(self):
        return self.code1.get_cda_format()


class Cell(BigIntegerPKModel):
    thtd_choice = (
        ('th', 'th'),
        ('td', 'td'),
    )
    row = models.ForeignKey('Row', models.DO_NOTHING, blank=True, null=True)
    col = models.ForeignKey('Col', models.DO_NOTHING, blank=True, null=True)
    label = models.ForeignKey('Label', models.DO_NOTHING, blank=True, null=True)
    code1 = models.ForeignKey('Code1', models.DO_NOTHING, blank=True, null=True)
    content = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'cell'

    def __str__(self):
        return 'Table {} row:{} col:{}'.format(self.row.table, self.row.number, self.col.number)

    def get_code1(self, idsection):
        xhtml = '<label>'
        xhtml += '<a href="label/{}/code1/{}?prettyxml">{}</a>'.format(self.id, self.code1.id, self.code1.text)
        xhtml += '<a href="#" name="option.href.{}.{}"></a>'.format(idsection, self.id)
        xhtml += '</label>'
        return xhtml

    def get_content_cda(self):
        xhtml = '<content>{}</content>'.format(self.content)
        return xhtml


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
    xhtml5 = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'articlehtml'

    def __str__(self):
        return self.titulo

    def check_xhtml5(self):
        if 'article' in self.xhtml5:
            return 'YES'
        else:
            return None

    def get_xhtml5(self, idsection):
        return self.generate_xhtml5(self.xhtml5, idsection)

    def generate_xhtml5(self, xhtml5, idsection):
        hrefs = re.findall('<a href="(.+?)"/>', xhtml5)
        for href in hrefs:
            if 'label' in href:
                label = Label.objects.get(id=href.split('/')[-1])
                label_replace = re.compile('<a href="{}"/>'.format(href))
                xhtml5 = label_replace.sub(label.get_xhtml(idsection=idsection), xhtml5)
            elif 'table' in href:
                table = Table.objects.get(id=href.split('/')[-1])
                table_replace = re.compile('<a href="{}"/>'.format(href))
                xhtml5 = table_replace.sub(table.get_xhtml(idsection=idsection), xhtml5)
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

    def check_article_xhtml5(self):
        if self.article is None:
            return None
        else:
            return self.article.check_xhtml5()

    def get_article_xhtml(self):
        return self.article.get_xhtml5(idsection=self.idattribute)


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

    def get_patientRole(self):
        xml_cda = '<patientRole>'
        xml_cda += '<id extension="{}" root="{}"/>'.format(self.pid, self.poid)
        xml_cda += '<addr>'
        xml_cda += '<state>{}</state>'.format(self.pregion)
        xml_cda += '<city>{}</city>'.format(self.pciudad)
        # xml_cda += '<additionalLocator nullFlavor="NA"/>'
        xml_cda += '</addr>'
        xml_cda += '<patient>'
        xml_cda += '<name>'
        if '^' in self.pnombre:
            last_name, first_name = self.pnombre.split('^')
            xml_cda += '<given>{}</given>'.format(first_name)
            xml_cda += '<family>{}</family>'.format(last_name)
        else:
            xml_cda += '<familyname>{}</familyname>'.format(self.pnombre)
        xml_cda += '</name>'
        if self.psexo == 'M':
            xml_cda += '<administrativeGenderCode code="1" codeSystem="2.16.858.2.10000675.69600"'
            xml_cda += ' codeSystemName="UNAOID" displayName="{}"/>'.format(self.psexo)
        elif self.psexo == 'F':
            xml_cda += '<administrativeGenderCode code="2" codeSystem="2.16.858.2.10000675.69600"'
            xml_cda += ' codeSystemName="UNAOID" displayName="{}"/>'.format(self.psexo)
        else:
            xml_cda += '<administrativeGenderCode code="9" codeSystem="2.16.858.2.10000675.69600"'
            xml_cda += ' codeSystemName="UNAOID" displayName="No información"/>'
        xml_cda += '<birthTime value="{}"/>'.format(self.pnacimiento)
        xml_cda += '</patient>'
        xml_cda += '</patientRole>'
        return xml_cda


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
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    iname = models.CharField(max_length=255, blank=True, null=True)
    ioid = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        db_table = 'firma'

    def get_cda_format(self):
        xml_cda = '<author><time value="{}"/>'.format(self.fecha.strftime("%Y%m%d%H%M%S"))
        xml_cda += '<assignedAuthor>'
        xml_cda += '<id root="{}"/>'.format(self.user.id)
        xml_cda += '<assignedPerson>'
        xml_cda += '<name>'
        xml_cda += '<given>{}</given>'.format(self.user.first_name)
        xml_cda += '<family>{}</family>'.format(self.user.last_name)
        xml_cda += '</name>'
        xml_cda += '</assignedPerson>'
        xml_cda += '<representedOrganization>'
        xml_cda += '<id root="{}"/>'.format(self.ioid)
        xml_cda += '<name>{}</name>'.format(self.iname)
        xml_cda += '</representedOrganization>'
        xml_cda += '</assignedAuthor></author>'
        return xml_cda


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
