# Лабораторная работа 3. RPC. gRPC. Protobuf
В разработке...
## Постановка задачи
Изучите [пример](https://drive.google.com/file/d/1Jm3R78LdC6KRbwZVnBy9fzYP8_r6RchC/view) в колабе и выполните шаги, указанные там. Предоставьте ссылку на репозиторий GitHub со всеми необходимыми компонентами для развертывания. 

В репозитории отразите отчет с помощью файла с разметкой Markdown, где демонстрировался бы процесс развертывания и работы сервиса.

Замечание

Предполагается, что эта работа выполняется локально, не смотря на то, что написано в самом колабе. Поэтому адаптируйте с помощью LLM те команды по настройке среды, которые вы найдете в борде. Они изменятся минимально. 

## Структура проекта
```
├── README.md                  
├── compose.yaml               
├── .dockerignore                                 
├── protos/
│   └── recommendations.proto
├── marketplace/
│   ├── Dockerfile             
│   ├── marketplace.py         
│   ├── requirements.txt       
│   └── test_marketplace.py    
└── recommendations/
    ├── Dockerfile             
    ├── recommendations.py     
    └── requirements.txt       
```