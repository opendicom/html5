from rest_framework import serializers
from radiologo import models


class CodesystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Codesystem
        fields = '__all__'


class ScriptelementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Scriptelement
        fields = '__all__'


class HeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Header
        fields = '__all__'


class FooterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Footer
        fields = '__all__'


class ArticlehtmlSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Articlehtml
        fields = '__all__'


class CodeSerializer(serializers.ModelSerializer):
    codesystem = CodesystemSerializer(source='fkcodesystem', many=False, read_only=True)
    class Meta:
        model = models.Code
        fields = ('id', 'code', 'displayname', 'fkcodesystem', 'codesystem')


class EstudioSerializer(serializers.ModelSerializer):
    code = CodeSerializer(source="fkcode", many=False, read_only=True)
    class Meta:
        model = models.Estudio
        fields = ('id', 'modalidad', 'fkcode', 'code')


class PlantillaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Plantilla
        fields = '__all__'


class PlantillagruposldapSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Plantillagruposldap
        fields = '__all__'


class SeccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Seccion
        fields = '__all__'


class SelectoptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Selectoption
        fields = '__all__'


class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Entry
        fields = '__all__'


class QualifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Qualifier
        fields = '__all__'


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Value
        fields = '__all__'


class AutenticadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Autenticado
        fields = '__all__'


class SecSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sec
        fields = '__all__'


class SusbsecSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Susbsec
        fields = '__all__'


class SusbsubsecSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Susbsubsec
        fields = '__all__'


class FirmaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Firma
        fields = '__all__'


class SubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Submit
        fields = '__all__'
