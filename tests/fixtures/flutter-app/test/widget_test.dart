import 'package:flutter_test/flutter_test.dart';
import 'package:trailmate/main.dart';

void main() {
  testWidgets('home shows title', (tester) async {
    await tester.pumpWidget(const TrailmateApp());
    expect(find.text('Your trails'), findsOneWidget);
  });
}
