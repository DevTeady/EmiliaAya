FROM registry.gitlab.com/harukanetwork/oss/harukaaya:dockerstation

RUN git clone https://github.com/DevTeady/HarukaAya-MOD /data/HarukaAya

COPY ./config.yml /data/HarukaAya

WORKDIR /data/HarukaAya

CMD ["python", "-m", "haruka"]
