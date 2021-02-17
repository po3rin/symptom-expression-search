ARG sudachi_dict_type="core"
ARG dict_version="20201223"

# 辞書のビルド
FROM python:3.9.0-slim-buster as dict_builder

ARG sudachi_dict_type
ARG dict_version

WORKDIR /home

COPY src/sudachi_user_dict.txt ./

RUN apt-get update && \
    apt-get install -y curl unzip build-essential && \
    curl -O -L https://github.com/WorksApplications/elasticsearch-sudachi/releases/download/v2.1.0/analysis-sudachi-7.10.1-2.1.0.zip && \
    unzip analysis-sudachi-7.10.1-2.1.0.zip && \
    curl -O -L http://sudachi.s3-website-ap-northeast-1.amazonaws.com/sudachidict/sudachi-dictionary-${dict_version}-${sudachi_dict_type}.zip && \
    unzip sudachi-dictionary-${dict_version}-${sudachi_dict_type}.zip && \
    cp sudachi-dictionary-${dict_version}/system_${sudachi_dict_type}.dic ./system_core.dic && \
    pip install sudachipy && pip install sudachidict_core && \
    sudachipy ubuild sudachi_user_dict.txt -o sudachi_user.dic

 
# プラグインを読み込んだElasticsearch
FROM docker.elastic.co/elasticsearch/elasticsearch:7.10.1

ARG sudachi_dict_type
ARG dict_version
ARG sudachi_dir=/usr/share/elasticsearch/config/sudachi/
ARG config_dir=/usr/share/elasticsearch/config/

# # if you want to customize config, you must comment out.
# COPY config/elasticsearch.yml ${config_dir}
# COPY config/log4j2.properties ${config_dir}

COPY config/sudachi.json ${sudachi_dir}
COPY --from=dict_builder /home/system_core.dic ${sudachi_dir}
COPY --from=dict_builder /home/sudachi_user.dic ${sudachi_dir}
COPY --from=dict_builder /home/analysis-sudachi-7.10.1-2.1.0.zip /usr/share/elasticsearch/

RUN bin/elasticsearch-plugin install file:///usr/share/elasticsearch/analysis-sudachi-7.10.1-2.1.0.zip && \
    rm /usr/share/elasticsearch/analysis-sudachi-7.10.1-2.1.0.zip
