FROM gsi

# Copy the code
COPY --chown=rcs:rcs test-service/RTS.py /opt/code/

# Run parameters
WORKDIR /opt/code

# Make sure venv is activated
ENV PATH="/opt/venv/bin:$PATH"

# Run the RCS Test Service
CMD ["python", "RTS.py"]
