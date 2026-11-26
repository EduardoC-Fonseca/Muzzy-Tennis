enum TipoSuperficie {
  saibro('saibro', 'Saibro'),
  rapida('rapida', 'Rápida'),
  grama('grama', 'Grama'),
  sintetico('sintetico', 'Sintética');

  final String api;
  final String descricao;

  const TipoSuperficie(this.api, this.descricao);
}