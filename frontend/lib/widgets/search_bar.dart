import 'package:google_fonts/google_fonts.dart';
import 'package:material_ui/material_ui.dart';
import 'package:muzzi_tennis/core/app_theme.dart';
import 'package:muzzi_tennis/models/tipo_superficie.dart';

class SearchBarMuzziTennis extends StatefulWidget {
  const SearchBarMuzziTennis({super.key});

  @override
  State<SearchBarMuzziTennis> createState() => _BarraPesquisaState();
}

class _BarraPesquisaState extends State<SearchBarMuzziTennis> {
  String cidade = '';
  TipoSuperficie? superficieSelecionada;

  final quadras = [
    {
      'nome': 'Quadra Central',
      'cidade': 'João Monlevade',
      'superficie': TipoSuperficie.saibro,
    },
    {
      'nome': 'Arena Tennis',
      'cidade': 'Belo Horizonte',
      'superficie': TipoSuperficie.rapida,
    },
    {
      'nome': 'Clube Tennis',
      'cidade': 'João Monlevade',
      'superficie': TipoSuperficie.rapida,
    },
  ];

  String normalizarCidade(String texto) {
  return texto
      .toLowerCase()
      .trim()
      .replaceAll(RegExp(r'[áàâãä]'), 'a')
      .replaceAll(RegExp(r'[éèêë]'), 'e')
      .replaceAll(RegExp(r'[íìîï]'), 'i')
      .replaceAll(RegExp(r'[óòôõö]'), 'o')
      .replaceAll(RegExp(r'[úùûü]'), 'u')
      .replaceAll('ç', 'c')
      .replaceAll(RegExp(r'\s+'), ' ');
  }

  @override 
  Widget build(BuildContext context){
    return Row(
      children: [
        SizedBox(
          width: 350,
          child: TextField(
          onChanged: (valor){ 
            setState(() {
              cidade = valor;
            });
          },
          decoration: const InputDecoration(
            labelText: 'Cidade',
            hintText: 'Digite a cidade desejada',
            prefixIcon: Icon(Icons.map_outlined),
            border: OutlineInputBorder(),
          ),
        ),
        ),  
        SizedBox(
          width: 250,
          child: DropdownButtonFormField<TipoSuperficie>(
            initialValue: superficieSelecionada,
            isExpanded: true,
            decoration: const InputDecoration(
              labelText: 'Superfície',
              border: OutlineInputBorder(),
            ),
            hint: const Text('Qualquer tipo'),
            items: [
              const DropdownMenuItem<TipoSuperficie>(
                value: null,
                child: Text('Qualquer tipo'),
              ),
              ...TipoSuperficie.values.map((tipo) {
                return DropdownMenuItem<TipoSuperficie>(
                  value: tipo,
                  child: Text(tipo.descricao),
                );
              }),
            ],
            onChanged: (valor) {
              setState(() {
                superficieSelecionada = valor;
              });
            },
          ),
        ),
        const SizedBox(width: 16),
        SizedBox(
          height: 50,
          child: ElevatedButton.icon(
            onPressed: () {
              final resultados = quadras.where((quadra) {
                final cidadeQuadra = quadra['cidade'] as String;
                final superficieQuadra = quadra['superficie'];
                final cidadeNormalizada = normalizarCidade(cidade);
                final cidadeQuadraNormalizada = normalizarCidade(cidadeQuadra);
                final correspondeCidade = cidadeNormalizada.split(' ').every((palavra) => cidadeQuadraNormalizada.contains(palavra));
                final correspondeSuperficie = superficieSelecionada == null || superficieQuadra == superficieSelecionada;
                return correspondeCidade && correspondeSuperficie;
              }).toList();
              Navigator.pushNamed(
                context,
                '/quadras',
                arguments: resultados,
              );

              debugPrint('Quadras encontradas: ${resultados.length}');

              for (final quadra in resultados) {
                debugPrint('Quadra: ${quadra['nome']}');
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.verdeMuzziTennis,
              foregroundColor: AppTheme.fundoPreto,
              elevation: 0,
              padding: const EdgeInsets.symmetric(horizontal: 15),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              textStyle: GoogleFonts.barlowCondensed(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                letterSpacing: 1,
              ),
            ),
            icon: const Icon(Icons.search),
            label: const Text('BUSCAR QUADRAS'),
          ),
        ),
      ]
    );
  }
}