from django import forms
from .models import Loja, Tipomovimento, Grupo, Subgrupo, Produto, Movimentacao

class LojaForm(forms.ModelForm):
    class Meta:
        model = Loja
        fields = "__all__"


class TipoMovientoForm(forms.ModelForm):
    class Meta:
        model = Tipomovimento
        fields = "__all__"


class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = "__all__"


class SubGrupoForm(forms.ModelForm):
    class Meta:
        model = Subgrupo
        fields = "__all__"

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = "__all__"

class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = Movimentacao
        fields = "__all__"