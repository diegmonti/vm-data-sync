IMAGE_NAME = diegmonti/influx-data-sync

build:
	docker build -t $(IMAGE_NAME) .
	docker push $(IMAGE_NAME)

.PHONY: build
