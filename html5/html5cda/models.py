from __future__ import unicode_literals

from django.db import models


class Configuracion(models.Model):
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=200)


class Codesystem(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=16, blank=True, null=True)
    oid = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'codesystem'

    def __str__(self):
        return 'name: %s, oid: %s' % (self.name, self.oid)


class Scriptelement(models.Model):
    id = models.BigAutoField(primary_key=True)
    html = models.TextField(blank=True, null=True)
    titulo = models.CharField(max_length=64, blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    comentario = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'scriptelement'


class Header(models.Model):
    id = models.BigAutoField(primary_key=True)
    html = models.TextField(blank=True, null=True)
    titulo = models.CharField(max_length=64, blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    comentario = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'header'


class Footer(models.Model):
    id = models.BigAutoField(primary_key=True)
    html = models.TextField(blank=True, null=True)
    titulo = models.CharField(max_length=64, blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    comentario = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'footer'


class Articlehtml(models.Model):
    id = models.BigAutoField(primary_key=True)
    titulo = models.CharField(max_length=64, blank=True, null=True)
    descripcion = models.CharField(max_length=256, blank=True, null=True)
    html = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'articlehtml'

    def __str__(self):
        return 'Titulo: %s, descripcion: %s' % (self.titulo, self.descripcion)


class Code(models.Model):
    id = models.BigAutoField(primary_key=True)
    fkcodesystem = models.ForeignKey('Codesystem', models.DO_NOTHING, db_column='fkcodesystem', blank=True, null=True)
    code = models.CharField(max_length=16, blank=True, null=True)
    displayname = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'code'

    def __str__(self):
        return 'code: %s, displayname: %s' % (self.code, self.displayname)


class Estudio(models.Model):
    id = models.BigAutoField(primary_key=True)
    modalidad = models.CharField(max_length=5, blank=True, null=True)
    fkcode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcode', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estudio'


class Plantilla(models.Model):
    id = models.BigAutoField(primary_key=True)
    fkestudio = models.ForeignKey(Estudio, models.DO_NOTHING, db_column='fkestudio', blank=True, null=True)
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

    class Meta:
        managed = False
        db_table = 'plantilla'


class Plantillagruposldap(models.Model):
    id = models.BigAutoField(primary_key=True)
    fkplantilla = models.ForeignKey(Plantilla, models.DO_NOTHING, db_column='fkplantilla', blank=True, null=True)
    gdn = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plantillagruposldap'


class Headscript(models.Model):
    id = models.BigAutoField(primary_key=True)
    fkscript = models.ForeignKey('Scriptelement', models.DO_NOTHING, db_column='fkscript', blank=True, null=True)
    fkplantilla = models.ForeignKey('Plantilla', models.DO_NOTHING, db_column='fkplantilla', blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'headscript'


class Bodyscript(models.Model):
    id = models.BigAutoField(primary_key=True)
    fkscript = models.ForeignKey('Scriptelement', models.DO_NOTHING, db_column='fkscript', blank=True, null=True)
    fkplantilla = models.ForeignKey('Plantilla', models.DO_NOTHING, db_column='fkplantilla', blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'bodyscript'


class Plantillaheader(models.Model):
    id = models.BigAutoField(primary_key=True)
    fkheader = models.ForeignKey(Header, models.DO_NOTHING, db_column='fkheader', blank=True, null=True)
    fkplantilla = models.ForeignKey(Plantilla, models.DO_NOTHING, db_column='fkplantilla', blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plantillaheader'


class Plantillafooter(models.Model):
    id = models.BigAutoField(primary_key=True)
    fkfooter = models.ForeignKey(Footer, models.DO_NOTHING, db_column='fkfooter', blank=True, null=True)
    fkplantilla = models.ForeignKey(Plantilla, models.DO_NOTHING, db_column='fkplantilla', blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plantillafooter'


class Seccion(models.Model):
    id = models.BigAutoField(primary_key=True)
    fksection = models.ForeignKey('self', models.DO_NOTHING, db_column='fksection', blank=True, null=True)
    idseccion = models.CharField(max_length=4, blank=True, null=True)
    fkplantilla = models.ForeignKey(Plantilla, models.DO_NOTHING, db_column='fkplantilla', blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)
    templateuidroot = models.CharField(max_length=64, blank=True, null=True)
    selectcolor = models.CharField(max_length=16, blank=True, null=True)
    selecttitle = models.CharField(max_length=255, blank=True, null=True)
    inputchecked = models.CharField(max_length=2, blank=True, null=True)
    fkcode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcode', blank=True, null=True)
    fkarticlehtml = models.ForeignKey(Articlehtml, models.DO_NOTHING, db_column='fkarticlehtml', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'seccion'


class Selectoption(models.Model):
    id = models.BigAutoField(primary_key=True)
    fksection = models.ForeignKey(Seccion, models.DO_NOTHING, db_column='fksection', blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)
    value = models.CharField(max_length=64, blank=True, null=True)
    text = models.CharField(max_length=64, blank=True, null=True)
    selected = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'selectoption'


class Entry(models.Model):
    id = models.BigAutoField(primary_key=True)
    element = models.CharField(max_length=16, blank=True, null=True)
    elementclasscode = models.CharField(max_length=8, blank=True, null=True)
    elementmoodcode = models.CharField(max_length=8, blank=True, null=True)
    templateuid = models.CharField(max_length=64, blank=True, null=True)
    identry = models.CharField(max_length=64, blank=True, null=True)
    fkcode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcode', blank=True, null=True)
    textreferencevalue = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'entry'


class Qualifier(models.Model):
    id = models.BigAutoField(primary_key=True)
    fkentry = models.ForeignKey(Entry, models.DO_NOTHING, db_column='fkentry', blank=True, null=True)
    ordinal = models.IntegerField(blank=True, null=True)
    fkcode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcode', blank=True, null=True)
    valueoriginaltext = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'qualifier'


class Value(models.Model):
    id = models.BigAutoField(primary_key=True)
    fkentry = models.ForeignKey(Entry, models.DO_NOTHING, db_column='fkentry', blank=True, null=True)
    type = models.CharField(max_length=8, blank=True, null=True)
    fkcode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcode', blank=True, null=True)
    unit = models.CharField(max_length=16, blank=True, null=True)
    value = models.CharField(max_length=64, blank=True, null=True)
    nullflavor = models.CharField(db_column='nullFlavor', max_length=16, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'value'


class Autenticado(models.Model):
    id = models.BigAutoField(primary_key=True)
    fkautenticado = models.ForeignKey('self', models.DO_NOTHING, db_column='fkautenticado', blank=True, null=True,
                                      related_name="autenticado")
    fkplantilla = models.ForeignKey('Plantilla', models.DO_NOTHING, db_column='fkplantilla', blank=True, null=True,
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
    fkestudio = models.ForeignKey('Estudio', models.DO_NOTHING, db_column='fkestudio', blank=True, null=True)
    informetitulo = models.CharField(max_length=255, blank=True, null=True)
    informeuid = models.CharField(max_length=64, blank=True, null=True)
    custodianoid = models.CharField(max_length=64, blank=True, null=True)
    valoracion = models.CharField(max_length=64, blank=True, null=True)
    solicituduid = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'autenticado'


class Sec(models.Model):
    id = models.BigAutoField(primary_key=True)
    fkautenticado = models.ForeignKey(Autenticado, models.DO_NOTHING, db_column='fkautenticado', blank=True, null=True,
                                      related_name="secautenticado")
    fkcompcode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcompcode', blank=True, null=True,
                                   related_name="seccompcode")
    templateuid = models.CharField(max_length=64, blank=True, null=True)
    idsec = models.CharField(max_length=4, blank=True, null=True)
    fkseccode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkseccode', blank=True, null=True,
                                  related_name="seccode")
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sec'


class Susbsec(models.Model):
    id = models.BigAutoField(primary_key=True)
    fksec = models.ForeignKey(Sec, models.DO_NOTHING, db_column='fksec', blank=True, null=True)
    fkcompcode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcompcode', blank=True, null=True,
                                   related_name="fkcompcode")
    templateuid = models.CharField(max_length=64, blank=True, null=True)
    idsusbsec = models.CharField(max_length=4, blank=True, null=True)
    fksubseccode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fksubseccode', blank=True, null=True,
                                     related_name="fksubseccode")
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'susbsec'


class Susbsubsec(models.Model):
    id = models.BigAutoField(primary_key=True)
    fksubsec = models.ForeignKey(Susbsec, models.DO_NOTHING, db_column='fksubsec', blank=True, null=True,
                                 related_name="subsec")
    fkcompcode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fkcompcode', blank=True, null=True,
                                   related_name="compcode")
    templateuid = models.CharField(max_length=64, blank=True, null=True)
    idsusbsubsec = models.CharField(max_length=4, blank=True, null=True)
    fksubsubseccode = models.ForeignKey(Code, models.DO_NOTHING, db_column='fksubsubseccode', blank=True, null=True,
                                        related_name="subsubseccode")
    title = models.CharField(max_length=255, blank=True, null=True)
    text = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'susbsubsec'


class Firma(models.Model):
    id = models.BigAutoField(primary_key=True)
    fkinforme = models.ForeignKey('Submit', models.DO_NOTHING, db_column='fkinforme', blank=True, null=True)
    md5 = models.CharField(max_length=45, blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    udn = models.CharField(max_length=64, blank=True, null=True)
    uid = models.CharField(max_length=16, blank=True, null=True)
    uoid = models.CharField(max_length=64, blank=True, null=True)
    uname = models.CharField(max_length=255, blank=True, null=True)
    iname = models.CharField(max_length=255, blank=True, null=True)
    ioid = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'firma'


class Secentry(models.Model):
    id = models.BigAutoField(primary_key=True)
    ordinal = models.IntegerField(blank=True, null=True)
    fk = models.ForeignKey(Sec, models.DO_NOTHING, db_column='fk', blank=True, null=True)
    fkentry = models.ForeignKey(Entry, models.DO_NOTHING, db_column='fkentry', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'secentry'


class Submit(models.Model):
    id = models.BigAutoField(primary_key=True)
    fkplantilla = models.ForeignKey(Plantilla, models.DO_NOTHING, db_column='fkplantilla', blank=True, null=True)
    eiud = models.CharField(max_length=64, blank=True, null=True)
    eaccnum = models.CharField(max_length=16, blank=True, null=True)
    eaccoid = models.CharField(max_length=64, blank=True, null=True)
    urlparamsenviado = models.TextField(blank=True, null=True)
    urlparamsrecibido = models.TextField(blank=True, null=True)
    listoparaautenticacion = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'submit'


class Subsecentry(models.Model):
    id = models.BigAutoField(primary_key=True)
    ordinal = models.IntegerField(blank=True, null=True)
    fk = models.ForeignKey('Susbsec', models.DO_NOTHING, db_column='fk', blank=True, null=True)
    fkentry = models.ForeignKey(Entry, models.DO_NOTHING, db_column='fkentry', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subsecentry'


class Subsubsecentry(models.Model):
    id = models.BigAutoField(primary_key=True)
    ordinal = models.IntegerField(blank=True, null=True)
    fk = models.ForeignKey('Susbsubsec', models.DO_NOTHING, db_column='fk', blank=True, null=True)
    fkentry = models.ForeignKey(Entry, models.DO_NOTHING, db_column='fkentry', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'subsubsecentry'
