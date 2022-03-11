import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'package:dio/dio.dart';
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Blood counter',
      theme: ThemeData(
        primarySwatch: Colors.red,
      ),
      home: const MyHomePage(title: 'Blood Counter'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final String endPoint = 'http://10.0.2.2:5000/count';
  var jsonResponse;

  Future _choose(jsonResponse) async {
    File file;
    file = await ImagePicker.pickImage(
      source: ImageSource.gallery,
    );
    if (file != null) {
      _upload(file);
      setState(() {});
    }
  }

  void _upload(File file) async {
    String fileName = file.path.split('/').last;
    print(fileName);

    FormData data = FormData.fromMap({
      "file": await MultipartFile.fromFile(
        file.path,
        filename: fileName,
      ),
    });

    Dio dio = new Dio();

    dio.post(endPoint, data: data).then((response) {
      jsonResponse = jsonDecode(response.toString());
      print(jsonResponse);
      return jsonResponse;
    }).catchError((error) => print(error));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text("Counted Cells"),
            MaterialButton(
              color: Colors.redAccent,
              child: const Text("Pick Image from Camera",
                  style: TextStyle(
                      color: Colors.white, fontWeight: FontWeight.bold)),
              onPressed: () {
                setState(() {
                  data = _choose(jsonResponse);
                  print(data);
                });
              },
            ),
          ],
        ),
      ),
    );
  }
}
