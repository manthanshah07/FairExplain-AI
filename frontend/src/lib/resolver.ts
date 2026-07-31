import { z } from "zod"

export const zodResolver = <T extends z.ZodTypeAny>(schema: T) => async (data: any) => {
  try {
    const values = await schema.parseAsync(data);
    return { values, errors: {} };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        values: {},
        errors: error.issues.reduce((acc: any, currentError: z.ZodIssue) => {
          acc[currentError.path[0]] = { type: currentError.code, message: currentError.message };
          return acc;
        }, {}),
      };
    }
    return { values: {}, errors: {} };
  }
};
