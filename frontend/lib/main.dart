import 'package:material_ui/material_ui.dart';

void main() {
  runApp(const MuzziTennisApp());
}

class MuzziTennisApp extends StatelessWidget {
  const MuzziTennisApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Muzzi Tennis',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(),
      home: Scaffold(
        body: Center(
          child: Text('Bem-vindo ao Muzzi Tennis!'),
        ),
      ),
    );
  }
}