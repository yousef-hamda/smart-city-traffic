package city.smart.ingestion;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment;

/** Verifies that the Spring application context boots with the skeleton configuration. */
@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class ApplicationTests {

  @Test
  void contextLoads() {
    // Boots the full context; fails if any bean wiring or configuration is broken.
  }
}
