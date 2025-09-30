from pydantic import BaseModel, Field


# ===== CONSULTA FINANCEIRA =====

class ConsultaFinanceiraInput(BaseModel):
    cnpj: str = Field(..., description="CNPJ do cliente a ser buscado")


class ConsultaFinanceiraOutput(BaseModel):
    status: str = Field(..., description="Status da operação")
    mensagem: str | None = Field(default=None, description="Mensagem de erro se houver")
    cliente: dict | None = Field(default=None, description="Informações do cliente")
    pendencias: list[dict] | None = Field(default=None, description="Lista de pendências")
    total_pendencias: int | None = Field(default=None, description="Total de pendências")


# ===== ATUALIZAR BOLETO =====

class AtualizarBoletoInput(BaseModel):
    boleto_id: str = Field(..., description="ID do pagamento no Asaas")
    valor: float = Field(..., description="Valor do boleto")


class AtualizarBoletoOutput(BaseModel):
    status: str = Field(..., description="Status da operação")
    mensagem: str | None = Field(default=None, description="Mensagem de erro se houver")
    boleto_id: str | None = Field(default=None, description="ID do boleto")
    valor: float | None = Field(default=None, description="Valor do boleto")
    data_vencimento: str | None = Field(default=None, description="Nova data de vencimento")
    data_vencimento_original: str | None = Field(default=None, description="Data de vencimento original")
    link_boleto: str | None = Field(default=None, description="Link do boleto")
    link_fatura: str | None = Field(default=None, description="Link da fatura")
    numero_fatura: str | None = Field(default=None, description="Número da fatura")
    status_pagamento: str | None = Field(default=None, description="Status do pagamento")


# ===== REGISTRAR NEGOCIAÇÃO =====

class RegistrarNegociacaoInput(BaseModel):
    cnpj: str = Field(..., description="CNPJ do cliente (obrigatório)")
    detalhes: str = Field(..., description="Detalhes da negociação")


class RegistrarNegociacaoOutput(BaseModel):
    status: str = Field(..., description="Status da operação")
    mensagem: str | None = Field(default=None, description="Mensagem de retorno")


# ===== VERIFICAR NEGOCIAÇÃO =====

class VerificarNegociacaoInput(BaseModel):
    cnpj: str = Field(..., description="CNPJ do cliente para buscar negociações")


class VerificarNegociacaoOutput(BaseModel):
    status: str = Field(..., description="Status da operação")
    mensagem: str | None = Field(default=None, description="Mensagem de erro se houver")
    negociacoes: list[dict] | None = Field(default=None, description="Lista de negociações")
    total: int | None = Field(default=None, description="Total de negociações")


# ===== VALIDAR COMPROVANTE =====

class ValidarComprovanteInput(BaseModel):
    ocr_text: str = Field(..., description="Texto extraído do comprovante via OCR")


class ValidarComprovanteOutput(BaseModel):
    status: str = Field(..., description="Status da validação")
    mensagem: str = Field(..., description="Mensagem de retorno")
    valido: bool | None = Field(default=None, description="Se o comprovante é válido")
    confiabilidade: float | None = Field(default=None, description="Taxa de confiabilidade (0-1)")


# ===== TRANSFERIR HUMANO =====

class TransferirHumanoInput(BaseModel):
    contexto: str = Field(..., description="Contexto completo da conversa e motivo da transferência")


class TransferirHumanoOutput(BaseModel):
    status: str = Field(..., description="Status da operação")
    mensagem: str = Field(..., description="Mensagem de confirmação")
    ticket_id: str | None = Field(default=None, description="ID do ticket gerado")
